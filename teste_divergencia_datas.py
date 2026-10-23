import logging
from datetime import date
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from src.services.importador import buscar_ou_criar_processo


def executar_cenario(nome, data_banco, data_planilha, aviso_esperado):
    processo_existente = SimpleNamespace(
        data_processo=data_banco
    )

    consulta = MagicMock()
    consulta.filter.return_value = consulta
    consulta.first.return_value = processo_existente

    session = MagicMock()
    session.query.return_value = consulta

    area = SimpleNamespace(id=1, nome="Projeto")
    pendentes = set()

    with patch(
        "src.services.importador.logger"
    ) as logger_mock:
        resultado = buscar_ou_criar_processo(
            session=session,
            area=area,
            numero="TESTE-123",
            data_processo=data_planilha,
            nome_arquivo="PLANILHA PROJ TESTE.xlsx",
            quantidade=1,
            chaves_processos_pendentes=pendentes,
        )

        if aviso_esperado:
            assert logger_mock.warning.called, (
                f"{nome}: deveria registrar um aviso"
            )
        else:
            assert not logger_mock.warning.called, (
                f"{nome}: não deveria registrar um aviso"
            )

    assert resultado is False, (
        f"{nome}: não deveria criar outro processo"
    )

    assert not session.add.called, (
        f"{nome}: não deveria inserir processo"
    )

    assert processo_existente.data_processo == data_banco, (
        f"{nome}: a data existente foi modificada"
    )

    print(f"OK: {nome}")


def main():
    logging.disable(logging.CRITICAL)

    executar_cenario(
        "Datas iguais",
        date(2026, 8, 6),
        date(2026, 8, 6),
        False,
    )

    executar_cenario(
        "Datas diferentes",
        date(2026, 8, 5),
        date(2026, 8, 6),
        True,
    )

    executar_cenario(
        "Data ausente no banco",
        None,
        date(2026, 8, 6),
        True,
    )

    executar_cenario(
        "Data ausente na planilha",
        date(2026, 8, 6),
        None,
        True,
    )

    print("\nTodos os testes passaram.")


if __name__ == "__main__":
    main()
