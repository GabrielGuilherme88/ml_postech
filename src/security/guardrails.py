"""Guardrails de segurança para input e output do agente."""
import logging
import re
from presidio_analyzer import AnalyzerEngine, PatternRecognizer, Pattern
from presidio_analyzer.nlp_engine import NlpEngineProvider
from presidio_anonymizer import AnonymizerEngine

logger = logging.getLogger(__name__)

class InputGuardrail:
    """Valida e sanitiza input do usuário antes de enviar ao LLM."""
    INJECTION_PATTERNS = [
        r"ignore\s+(all\s+)?previous\s+instructions",
        r"you\s+are\s+now\s+a",
        r"system:\s*",
        r"<\|im_start\|>",
        r"\[INST\]",
        r"forget\s+(everything|all|your\s+instructions)",
        r"ignore\s+todas\s+as\s+instruções\s+anteriores",
        r"você\s+agora\s+é\s+um",
        r"ignorar\s+as\s+regras",
    ]

    def __init__(self, allowed_topics: list[str] | None = None):
        self.allowed_topics = allowed_topics or []
        self._compiled_patterns = [
            re.compile(p, re.IGNORECASE) for p in self.INJECTION_PATTERNS
        ]

    def validate(self, user_input: str) -> tuple[bool, str]:
        for pattern in self._compiled_patterns:
            if pattern.search(user_input):
                logger.warning("Prompt injection detectado: %s", user_input[:100])
                return False, "Input bloqueado: padrão suspeito detectado."

        if len(user_input) > 4096:
            return False, "Input bloqueado: excede tamanho máximo (4096 chars)."
        return True, "OK"

class OutputGuardrail:
    """Valida e sanitiza output do LLM antes de retornar ao usuário."""
    def __init__(self, language: str = "pt"):
        # Configurar engine NLP para português
        configuration = {
            "nlp_engine_name": "spacy",
            "models": [{"lang_code": "pt", "model_name": "pt_core_news_lg"}],
        }
        provider = NlpEngineProvider(nlp_configuration=configuration)
        nlp_engine = provider.create_engine()
        
        self.analyzer = AnalyzerEngine(
            nlp_engine=nlp_engine, 
            supported_languages=["pt"], 
            default_score_threshold=0.4
        )
        self.anonymizer = AnonymizerEngine()
        self.language = language
        self._add_custom_recognizers()

    def _add_custom_recognizers(self):
        """Adiciona reconhecedores para documentos brasileiros."""
        # Reconhecedor de CPF
        cpf_pattern = Pattern(
            name="cpf_pattern",
            regex=r"\d{3}\.\d{3}\.\d{3}-\d{2}|\d{11}",
            score=0.5
        )
        cpf_recognizer = PatternRecognizer(
            supported_entity="BR_CPF",
            patterns=[cpf_pattern],
            supported_language="pt"
        )
        self.analyzer.registry.add_recognizer(cpf_recognizer)

    def sanitize(self, llm_output: str) -> str:
        try:
            results = self.analyzer.analyze(
                text=llm_output,
                language=self.language,
                entities=["PERSON", "EMAIL_ADDRESS", "PHONE_NUMBER", "BR_CPF"],
            )
        except Exception as e:
            logger.error("Erro no AnalyzerEngine: %s. Pulando sanitização.", e)
            return llm_output

        if results:
            logger.warning("PII detectado no output: %d entidades", len(results))
            anonymized = self.anonymizer.anonymize(
                text=llm_output,
                analyzer_results=results,
            )
            return anonymized.text
        return llm_output
