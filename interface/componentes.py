import streamlit as st


def titulo(texto: str):

    st.subheader(texto)


def mensagem_sucesso(texto: str):

    st.success(texto)


def mensagem_erro(texto: str):

    st.error(texto)


def mensagem_aviso(texto: str):

    st.warning(texto)
