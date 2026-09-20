import re

import streamlit as st

st.set_page_config(page_title="Rota H", layout="centered")

st.markdown(
    """
    <style>
    [data-testid="stAppViewContainer"] { background-color: #f5f6f7; }
    [data-testid="stHeader"] { background-color: rgba(0,0,0,0); }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Cartões de status — cor é reservada para significado clínico:
# vermelho = ação crítica, verde = dentro da meta, cinza = neutro/aguardando.
# ---------------------------------------------------------------------------
_CORES = {
    "acao": ("#dc2626", "rgba(220, 38, 38, 0.05)"),
    "ok": ("#16a34a", "rgba(22, 163, 74, 0.05)"),
    "neutro": ("#d1d5db", "rgba(0, 0, 0, 0.015)"),
}


def _md_inline(texto):
    texto = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", texto)
    texto = re.sub(r"\*(.+?)\*", r"<em>\1</em>", texto)
    return texto


def _render_corpo(texto):
    linhas = [l.strip() for l in texto.strip().split("\n") if l.strip()]
    partes = []
    buffer_bullets = []
    for linha in linhas:
        linha = _md_inline(linha)
        if linha.startswith("- "):
            buffer_bullets.append(f"<li>{linha[2:]}</li>")
        else:
            if buffer_bullets:
                partes.append(f"<ul style='margin:0.3rem 0 0 1.1rem; padding:0;'>{''.join(buffer_bullets)}</ul>")
                buffer_bullets = []
            partes.append(f"<div>{linha}</div>")
    if buffer_bullets:
        partes.append(f"<ul style='margin:0.3rem 0 0 1.1rem; padding:0;'>{''.join(buffer_bullets)}</ul>")
    return "".join(partes)


def cartao(texto, tipo="neutro"):
    borda, fundo = _CORES.get(tipo, _CORES["neutro"])
    st.markdown(
        f"""
        <div style='border:1px solid {borda}; background-color:{fundo}; color:#1a1a1a;
        border-radius:8px; padding:0.7rem 1rem; margin:0.4rem 0; font-size:0.95rem;'>
        {_render_corpo(texto)}</div>
        """,
        unsafe_allow_html=True,
    )


def avaliar_gate(chave):
    """Pergunta o próximo passo; retorna True para liberar a próxima etapa do algoritmo."""
    status = st.radio(
        "Próximo passo:",
        ["Mantém sangramento", "Resolvido"],
        index=None,
        key=chave,
    )
    if status == "Resolvido":
        cartao("Sangramento resolvido. Manter medidas gerais (cálcio, pH, temperatura).", "ok")
        return False
    return status == "Mantém sangramento"


# ---------------------------------------------------------------------------
# Cabeçalho
# ---------------------------------------------------------------------------
st.markdown(
    """
    <div style='background-color:#8b0000; border:1px solid #660000; border-radius:12px;
                padding:0.7rem 1rem; text-align:center; margin-bottom:0.4rem;'>
        <span style='font-size:2rem; font-weight:800; color:#ffffff;'>Rota H</span><br>
        <span style='font-size:0.85rem; color:#ffffff; opacity:0.8;'>Roteiro do Código H guiado por ROTEM</span>
    </div>
    """,
    unsafe_allow_html=True,
)

_, col_info = st.columns([9, 1])
with col_info:
    with st.popover("ℹ️"):
        st.caption(
            "Ferramenta de apoio baseada no protocolo institucional. Não substitui o "
            "julgamento clínico nem a avaliação de um especialista."
        )

cartao(
    "**Prioridade em qualquer sangramento ativo:**\n"
    "- Cálcio iônico **> 1,0–1,1 mmol/L** (corrigir com cloreto de cálcio; monitorar e manter "
    "na faixa normal)\n"
    "- pH **> 7,2**\n"
    "- Temperatura **> 35–36 °C**\n"
    "- Considerar sangramento de etiologia **cirúrgica** → acionar **código cirúrgico**",
    "neutro",
)

# ---------------------------------------------------------------------------
# Passo 1 — medidas gerais e gatilhos clínicos
# ---------------------------------------------------------------------------
with st.expander("Passo 1 — Considerações gerais (marque o que se aplica)"):
    cumarinico = st.checkbox("Intoxicação cumarínica (AVK) / necessidade de reversão de urgência")
    doac = st.checkbox("Uso de anticoagulante oral direto (DOAC)")
    uremia_antiagregacao = st.checkbox("Sangramento por uremia ou antiagregação plaquetária")
    trauma_agudo = st.checkbox("Trauma agudo, nas primeiras 3 horas")
    hpp = st.checkbox("Hemorragia pós-parto (HPP), dentro de 3 horas")
    pos_cardiaca_vascular = st.checkbox(
        "Pós-operatório de cirurgia cardíaca ou cirurgia vascular arterial"
    )

    if trauma_agudo or hpp:
        st.caption(
            "Ácido tranexâmico é conduta **empírica** nesses contextos — não depende do "
            "resultado do ROTEM (a lise ao ROTEM tem baixa sensibilidade para hiperfibrinólise)."
        )

    st.markdown(
        "- Levantar história clínica: coagulopatia conhecida, uso de anticoagulantes/"
        "antiagregantes, AINE ou fitoterápicos\n"
        "- Concentrado de hemácias conforme julgamento clínico"
    )

    peso = st.number_input("Peso do paciente (kg)", min_value=1.0, max_value=300.0, value=70.0, step=1.0)

    acoes_passo1 = []
    if cumarinico:
        acoes_passo1.append(
            f"Considere reversão de cumarínico: **CCP 25 UI/kg** (~{25 * peso:.0f} UI) **+ Vitamina K**"
        )
    if uremia_antiagregacao:
        acoes_passo1.append(f"Considere **DDAVP 0,3 mcg/kg** (~{0.3 * peso:.1f} mcg)")
    if trauma_agudo:
        acoes_passo1.append("Considere **ácido tranexâmico**: 1 g em 10 min + 1 g em 8 h")
    if hpp:
        acoes_passo1.append(
            "Considere **ácido tranexâmico 1 g IV**, o mais precocemente possível; "
            "repetir 1 g se sangramento persistir após 30 min ou recorrer em 24 h"
        )
    if doac:
        acoes_passo1.append(
            "Considere reversão específica de DOAC: **andexanet alfa** (inibidores de Xa) ou "
            "**idarucizumabe** (dabigatrana); se antídoto específico indisponível, considere "
            f"**CCP 25 a 50 UI/kg** (~{25 * peso:.0f} a {50 * peso:.0f} UI) conforme disponibilidade institucional"
        )
    if pos_cardiaca_vascular:
        acoes_passo1.append("Considere **protamina 50 a 100 mg**")

    if acoes_passo1:
        texto_acoes = "**Condutas indicadas pelo contexto:**\n" + "\n".join(f"- {a}" for a in acoes_passo1)
        cartao(texto_acoes, "acao")

# ---------------------------------------------------------------------------
# Passo 2 — qual painel de ROTEM solicitar
# ---------------------------------------------------------------------------
with st.expander("Passo 2 — Qual ROTEM solicitar"):
    contexto = st.selectbox(
        "Contexto clínico",
        [
            "Cirurgia geral / paciente clínico",
            "Trauma agudo ou subagudo",
            "Paciente obstétrica",
            "Cirurgia vascular",
            "Cirurgia cardíaca",
            "Transplante hepático completo ou suspeita de hiperfibrinólise",
            "Transplante hepático normal",
        ],
    )

    painel_por_contexto = {
        "Cirurgia geral / paciente clínico": "EXTEM + FIBTEM",
        "Trauma agudo ou subagudo": "EXTEM + FIBTEM",
        "Paciente obstétrica": "EXTEM + FIBTEM",
        "Cirurgia vascular": "INTEM + FIBTEM",
        "Cirurgia cardíaca": "INTEM + FIBTEM",
        "Transplante hepático completo ou suspeita de hiperfibrinólise": "EXTEM + FIBTEM + APTEM",
        "Transplante hepático normal": "EXTEM + FIBTEM",
    }

    painel_base = painel_por_contexto[contexto]
    susp_fibrinolise_panel = st.checkbox("Suspeita de hiperfibrinólise → incluir APTEM")
    susp_heparina_panel = st.checkbox("Suspeita de heparina → incluir HEPTEM")

    extras = []
    if susp_fibrinolise_panel and "APTEM" not in painel_base:
        extras.append("APTEM")
    if susp_heparina_panel and "HEPTEM" not in painel_base:
        extras.append("HEPTEM")
    painel_final = painel_base + ("".join(f" + {e}" for e in extras))

    st.markdown(f"**Painel recomendado:** {painel_final}")

# ---------------------------------------------------------------------------
# Avaliação sequencial do ROTEM — um passo de cada vez
# ---------------------------------------------------------------------------
st.header("Avaliação sequencial do ROTEM")
st.caption(
    "Cada passo só deve ser avaliado depois que o anterior foi corrigido e o "
    "sangramento se mantém — um EXTEM A5/CT alterado pode ser apenas reflexo de um "
    "fibrinogênio ainda não corrigido, por exemplo. A ordem prioriza corrigir a geração "
    "de trombina (fibrinogênio → fatores/heparina) antes de indicar plaquetas, o recurso "
    "mais escasso e de maior risco imunológico/infeccioso."
)

# --- Passo 3: FIBTEM — fibrinogênio ----------------------------------------
st.subheader("Passo 3 — Fibrinogênio (FIBTEM A5/A10 abaixo da meta)")
col1, col2 = st.columns(2)
with col1:
    fibtem_a5 = st.number_input(
        "FIBTEM A5 (mm) — opcional", min_value=0.0, value=None, placeholder="mm", key="fibtem_a5"
    )
with col2:
    fibtem_a10 = st.number_input(
        "FIBTEM A10 (mm)", min_value=0.0, value=None, placeholder="mm", key="fibtem_a10"
    )

fibtem_baixo = (fibtem_a5 is not None and fibtem_a5 < 9) or (
    fibtem_a10 is not None and fibtem_a10 < 9
)
fibtem_valor = fibtem_a10 if fibtem_a10 is not None else fibtem_a5

prosseguir = False
if fibtem_a5 is None and fibtem_a10 is None:
    st.caption("Aguardando valor de FIBTEM A5/A10.")
elif fibtem_baixo:
    crio_dose = peso / 10
    cartao(
        f"FIBTEM = {fibtem_valor:.0f} mm (< 9 mm) → considere repor fibrinogênio: concentrado de "
        f"fibrinogênio 2 a 6 g **ou** crioprecipitado 1 UI/10 kg (~{crio_dose:.0f} UI)",
        "acao",
    )
    prosseguir = avaliar_gate("gate_fibrinogenio")
else:
    cartao(f"FIBTEM = {fibtem_valor:.0f} mm — dentro da meta populacional.", "ok")
    prosseguir = True

# --- Passo 4: fatores de coagulação e heparina/HEPTEM ----------------------
if prosseguir:
    st.subheader(
        "Passo 4 — Geração de trombina (CT) / efeito da heparina, com fibrinogênio já corrigido"
    )

    ccp_min, ccp_max = 20 * peso, 25 * peso
    pfc_min, pfc_max = 15 * peso, 20 * peso

    st.markdown("**EXTEM**")
    extem_ct = st.number_input(
        "EXTEM CT (s)", min_value=0.0, value=None, placeholder="s", key="extem_ct"
    )
    if extem_ct is None:
        st.caption("Aguardando EXTEM CT.")
    elif extem_ct > 79:
        cartao(
            "EXTEM CT > 79 s, com fibrinogênio corrigido → considerar deficiência de fatores de "
            f"coagulação → considere **CCP 20 a 25 UI/kg** (~{ccp_min:.0f} a {ccp_max:.0f} UI) "
            f"**ou PFC 15 a 20 mL/kg** (~{pfc_min:.0f} a {pfc_max:.0f} mL) se CCP indisponível",
            "acao",
        )
    else:
        cartao("EXTEM CT dentro da meta.", "ok")

    st.markdown("**INTEM**")
    intem_ct = st.number_input(
        "INTEM CT (s)", min_value=0.0, value=None, placeholder="s", key="intem_ct"
    )
    if intem_ct is None:
        st.caption("Aguardando INTEM CT.")
    elif intem_ct > 240:
        cartao(
            "INTEM CT > 240 s, com fibrinogênio corrigido → considerar deficiência de fatores de "
            f"coagulação → considere **CCP 20 a 25 UI/kg** (~{ccp_min:.0f} a {ccp_max:.0f} UI) "
            f"**ou PFC 15 a 20 mL/kg** (~{pfc_min:.0f} a {pfc_max:.0f} mL) se CCP indisponível",
            "acao",
        )
        susp_heparina = st.checkbox("Suspeita de resíduo de heparina no sistema")
        if susp_heparina:
            cartao(
                "Suspeita de **resíduo de heparina** → avaliação exclusiva por **INTEM vs HEPTEM** "
                "— razão CT INTEM/HEPTEM ≥ 1,25 sugere efeito heparínico → considere **protamina "
                "titulada** conforme a razão encontrada. *(EXTEM/FIBTEM contêm polibreno, que já "
                "neutraliza heparina — CT do EXTEM prolongado não indica heparina residual.)*",
                "acao",
            )
    else:
        cartao("INTEM CT dentro da meta.", "ok")

    st.markdown("**Lise precoce (LI30/LI45) — apenas para confirmação/monitorização:**")
    lise_precoce = st.number_input(
        "Índice de lise (%) — LI30/LI45",
        min_value=0.0,
        value=None,
        placeholder="%",
        key="lise_precoce",
    )
    if lise_precoce is None:
        st.caption("Aguardando índice de lise (LI30/LI45).")
    elif lise_precoce > 15:
        cartao(f"Índice de lise = {lise_precoce:.0f}% (> 15%) — sugere hiperfibrinólise.", "acao")
    else:
        cartao(f"Índice de lise = {lise_precoce:.0f}% (≤ 15%).", "ok")
    st.caption(
        "Teste pouco sensível: um valor normal **não exclui** hiperfibrinólise. Por isso **não "
        "condicione o ácido tranexâmico a este resultado** — em trauma agudo, HPP e suspeita "
        "clínica o TXA já é empírico (Passo 1); o ROTEM aqui serve só para confirmar/monitorar."
    )

    prosseguir = avaliar_gate("gate_fatores")

# --- Passo 5: plaquetas -----------------------------------------------------
if prosseguir:
    st.subheader("Passo 5 — Plaquetas (EXTEM A5, com FIBTEM já normal)")
    extem_a5 = st.number_input(
        "EXTEM A5 (mm)", min_value=0.0, value=None, placeholder="mm", key="extem_a5"
    )
    em_antiagregante = st.checkbox("Paciente em uso de antiagregante plaquetário")

    prosseguir = False
    if extem_a5 is None:
        st.caption("Aguardando EXTEM A5.")
    elif extem_a5 < 40:
        texto_plaquetas = (
            f"EXTEM A5 = {extem_a5:.0f} mm (< 40 mm), com FIBTEM já normal → considere "
            "**transfundir plaquetas**"
        )
        if em_antiagregante:
            ddavp_dose = 0.3 * peso
            texto_plaquetas += (
                "\n- Uso de antiagregante → considere **Multiplate** (agregometria) para "
                f"confirmar disfunção plaquetária\n- Considere **DDAVP 0,3 mcg/kg** "
                f"(~{ddavp_dose:.1f} mcg)"
            )
        cartao(texto_plaquetas, "acao")
        prosseguir = avaliar_gate("gate_plaquetas")
    else:
        cartao(f"EXTEM A5 = {extem_a5:.0f} mm — dentro da meta.", "ok")
        prosseguir = True

# --- Passo 6: sangramento refratário ---------------------------------------
if prosseguir:
    st.subheader("Passo 6 — Sangramento refratário")
    cartao(
        "**Persistiu apesar de fibrinogênio, fatores/heparina e plaquetas corrigidos:**\n"
        "- Reavaliar sangramento de etiologia **cirúrgica**\n"
        "- Dosar/considerar deficiência de **Fator XIII**\n"
        "- Repetir **novo ROTEM**\n"
        "- **rFVIIa** como último recurso, após esgotadas as medidas anteriores\n"
        "- Manter corrigidos cálcio, pH e temperatura\n"
        "- **Solicitar avaliação do especialista**",
        "acao",
    )
