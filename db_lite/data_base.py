import pandas as pd
from datetime import datetime, timedelta
import random
import os

def generate_mock_data(n=100):
    data = []
    
    for i in range(n):
        # Lógica de Datas
        dt_pedido = datetime(2025, 1, 1) + timedelta(days=random.randint(0, 365))
        dt_finalizacao = dt_pedido + timedelta(days=random.randint(5, 15))
        
        # Chance de ser indeferido ou pago
        situacao = random.choice(['PAGO', 'INDEFERIDO', 'EM ANALISE'])
        dt_pagamento = dt_finalizacao + timedelta(days=2) if situacao == 'PAGO' else None
        dt_indeferimento = dt_finalizacao if situacao == 'INDEFERIDO' else None
        
        # Valores financeiros
        vl_informado = round(random.uniform(100.0, 5000.0), 2)
        vl_glosa = round(vl_informado * random.choice([0, 0.1, 0.2]), 2)
        vl_aprovado = round(vl_informado - vl_glosa, 2)
        
        row = {
            "dt_pedidoreembolso": dt_pedido.strftime('%Y-%m-%d'),
            "dt_pagamentocentralunimed": dt_pagamento.strftime('%Y-%m-%d') if dt_pagamento else "",
            "dt_indeferimentoreembolso": dt_indeferimento.strftime('%Y-%m-%d') if dt_indeferimento else "",
            "nr_contrato": f"CONTR-{random.randint(1000, 9999)}",
            "cd_empresacontrato": random.randint(100, 900),
            "nm_empresa": random.choice(["Empresa Alfa Ltda", "Beta Tech S.A.", "Gamma Servicos"]),
            "nr_beneficiario": f"001234{random.randint(10000, 99999)}",
            "nm_beneficiario": f"Beneficiario Exemplo {i}",
            "nm_grupoempresa": "Grupo Corporativo Nacional",
            "nm_tipocobranca": random.choice(["Pre-pagamento", "Custo Operacional"]),
            "nm_tipopreco": "Faixa Etaria",
            "cd_tipoproduto": random.randint(1, 5),
            "nm_tipoproduto": "Saude Suplementar",
            "ds_origembeneficiario": "RH Empresa",
            "dt_finalizacaoreembolso": dt_finalizacao.strftime('%Y-%m-%d'),
            "nr_comprovante": f"COMP-{random.randint(100000, 999999)}",
            "nm_cid": random.choice(["Z00", "M54", "J06", "K21"]),
            "nm_unidadenegocio": "Unidade Matriz",
            "nr_titular": f"001234{random.randint(10000, 99999)}",
            "nm_titular": f"Titular Exemplo {i}",
            "sg_tipoassociado": random.choice(["T", "D", "P"]),
            "nm_deparatipoproduto": "Plano Standard",
            "nm_plano": "Plano Global Adesao",
            "nm_planocartao": "GLOBAL NACIONAL",
            "nm_redeplano": "Rede Ampla",
            "nr_reembolso": 2026000000 + i,
            "cd_internacao": random.randint(1000, 5000),
            "nr_internacao": random.randint(1000, 5000),
            "cd_procedimento": f"4030{random.randint(100, 999)}",
            "ds_observacaoreembolso": "Solicitacao via App",
            "cd_funcao": random.choice([1, 2, 3]),
            "nm_funcao": "Medico Assistente",
            "nm_situacaoreembolso": situacao,
            "sg_situacaoreembolso": situacao[0],
            "sg_tiposituacao": "F",
            "cd_plano": str(random.randint(10, 50)),
            "cd_unimedlcat": 34,
            "nm_cidadeunimed": "Sao Paulo",
            "sg_ufunimed": "SP",
            "nm_motivoreembolso": "Consulta Medica",
            "ds_deparamotivoreembolso": "Ambulatorial",
            "cd_origemreembolso": 1,
            "nm_origemreembolso": "Portal do Beneficiario",
            "cd_motivoglosamanual": 0,
            "nm_itemmedico": "Consulta",
            "cd_grupoestatistico": "01",
            "nm_grupoestatistico": "Consultas",
            "nm_tratamento": "Tratamento Clinico",
            "ds_deparatipoatendimento": "Eletivo",
            "fl_inscricaofiscal": random.choice(["F", "J"]),
            "nr_inscricaofiscal": random.randint(10000000000, 99999999999),
            "nm_prestador": f"Dr(a) Prestador de Saude {i}",
            "cd_cbo": "225125",
            "nm_cbo": "Clinico Geral",
            "qt_informado": 1.00,
            "qt_glosa": 0.00,
            "qt_glosamanual": 0.00,
            "qt_aprovada": 1.00,
            "vl_informado": vl_informado,
            "vl_glosa": vl_glosa,
            "vl_glosamanual": 0.00,
            "vl_aprovado": vl_aprovado,
            "vl_reembolsado": vl_aprovado if situacao == 'PAGO' else 0.00,
            "nm_favorecido": f"Favorecido Nome {i}",
            "cd_banco": random.choice([1, 33, 237, 341]),
            "cd_agencia": "0001",
            "nr_digitoagencia": "1",
            "nr_contacorrente": f"{random.randint(10000, 99999)}",
            "nr_digitocontacorrente": "0",
            "cd_usuarioatualizacao": "SISTEMA",
            "nm_usuarioatualizacao": "Robo de Integracao",
            "nm_emailatualizacao": "contato@empresa.com.br",
            "nr_pedidoautorizacao": random.randint(100000, 999999),
            "cd_prestadorexecutante": f"EXEC-{random.randint(100,999)}",
            "nm_prestadorexecutante": f"Clinica Executante {i}",
            "fl_pendenciamento": "N"
        }
        data.append(row)
    
    df = pd.DataFrame(data)
    return df

if __name__ == "__main__":
    import sqlite3
    df = generate_mock_data(100)
    
    dir_path = os.path.dirname(os.path.abspath(__file__))
    # Como o data_base.py agora foi movido para a própria pasta db_lite, o bd fica na mesma pasta!
    db_path = os.path.join(dir_path, 'meu_banco_de_dados.db')
    db_path = os.path.abspath(db_path)
    
    # Garante que o diretório db_lite existe
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    # Salvar na base (usando append para apenas adicionar aos dados criados pela estrutura inicial)
    df.to_sql('pedidos_reembolso', conn, if_exists='append', index=False)
    conn.close()
    
    print(f"100 Arquivos hipoteticos gerados e inseridos com sucesso na tabela pedidos_reembolso em:\n{db_path}")