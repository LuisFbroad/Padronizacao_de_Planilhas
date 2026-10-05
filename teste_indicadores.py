import pandas as pd

from src.excel.leitor import LeitorExcel
from src.excel.padronizador import PadronizadorExcel
from src.services.indicadores import IndicadoresService

# ==========================================
# CAMINHO DO EXCEL
# ==========================================

CAMINHO_EXCEL = (
    r"C:\Users\GAGC\Desktop\Projeto_Planilha"
    r"\data\entrada\RELATÓRIO MENSAL PADRÃO.xlsx"
)


# ==========================================
# 1. LER EXCEL
# ==========================================

print("=" * 50)
print("TESTE DO SISTEMA DE INDICADORES")
print("=" * 50)

print("\n1. Lendo Excel...")

leitor = LeitorExcel(CAMINHO_EXCEL)

abas = leitor.listar_abas()

print("Abas encontradas:")

for aba in abas:
    print(f"- {aba}")


# ==========================================
# 2. LER A ABA PRINCIPAL
# ==========================================

print("\n2. Lendo aba principal...")

dados = leitor.ler_aba("RELATÓRIO MENSAL (NOVOS)")

print(f"Registros encontrados: {len(dados)}")

print(f"Colunas encontradas: {len(dados.columns)}")


# ==========================================
# 3. PADRONIZAR
# ==========================================

print("\n3. Padronizando colunas...")

padronizador = PadronizadorExcel()

dados = padronizador.padronizar(dados)

print("Colunas padronizadas:")

for coluna in dados.columns:
    print(f"- {coluna}")


# ==========================================
# 4. CRIAR SERVIÇO DE INDICADORES
# ==========================================

print("\n4. Criando serviço de indicadores...")

indicadores = IndicadoresService(dados)


# ==========================================
# 5. CONTAR INDICADORES
# ==========================================

print("\n5. Contando indicações...")

resultado = indicadores.contar_indicacoes("Primária")


print("\nRESULTADO:")
print(resultado.to_string(index=False))


# ==========================================
# 6. TOTAL DE INDICAÇÕES
# ==========================================

total = indicadores.total_indicacoes("Primária")

print(f"\nTotal de indicações: {total}")


# ==========================================
# 7. QUANTIDADE DE INDICADORES
# ==========================================

quantidade = indicadores.quantidade_indicadores("Primária")

print(f"Quantidade de indicadores: {quantidade}")


print("\n" + "=" * 50)
print("TESTE FINALIZADO")
print("=" * 50)
