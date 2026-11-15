"""Gera o PTAM de exemplo (dados fictícios) em HTML, com todos os cálculos.

Uso: python3 gerar_relatorio.py  -> cria relatorio-ptam-exemplo.html
"""
import math
import statistics as st
from pathlib import Path

# ---------------------------------------------------------------- dados
AVALIANDO = dict(
    area=68.0, tipo="Apartamento residencial", dorm=2, suites=1, vagas=1, idade=9,
    endereco="Rua das Acácias, nº 120, Apto 302, Bairro Jardim Primavera, Cidade Exemplo/SC, CEP 88000-000",
    matricula="Matrícula nº 45.678 – 1º Registro de Imóveis de Cidade Exemplo",
    inscricao="Inscrição imobiliária nº 01.02.033.0456.001",
)
FATOR_OFERTA = 0.90
# endereço, fonte, área, valor ofertado, F.loc, F.padrão, F.conserv, dorm, vagas, idade
COMPARAVEIS = [
    ("Rua das Acácias, 210 – Apto 401", "Imobiliária Horizonte", 72.0, 505000, 1.00, 1.00, 1.00, 2, 1, 8),
    ("Rua dos Ipês, 88 – Apto 203", "Portal de anúncios", 64.5, 402000, 1.05, 1.00, 1.00, 2, 1, 10),
    ("Av. Central, 1.540 – Apto 702", "Corretor autônomo", 75.3, 560000, 0.95, 0.95, 1.00, 2, 1, 5),
    ("Rua das Palmeiras, 45 – Apto 104", "Imobiliária Lar Certo", 61.0, 410000, 1.00, 1.05, 1.05, 2, 1, 14),
    ("Rua Ver. Antônio Lima, 300 – Apto 502", "Portal de anúncios", 70.2, 455000, 1.00, 1.00, 1.00, 2, 1, 9),
    ("Rua dos Ipês, 150 – Apto 301", "Imobiliária Horizonte", 66.8, 470000, 1.05, 1.00, 0.95, 2, 1, 12),
    ("Rua das Acácias, 77 – Apto 205", "Imobiliária Lar Certo", 69.0, 438000, 1.00, 1.00, 1.00, 2, 1, 9),
    ("Rua Bela Vista, 510 – Apto 603", "Corretor autônomo", 80.0, 585000, 0.95, 1.00, 1.00, 3, 1, 6),
]
T80 = {2: 3.078, 3: 1.886, 4: 1.638, 5: 1.533, 6: 1.476, 7: 1.440, 8: 1.415, 9: 1.397,
       10: 1.383, 11: 1.372, 12: 1.363, 13: 1.356, 14: 1.350, 15: 1.345}  # t-Student bicaudal 80%, por graus de liberdade

# ------------------------------------------------------------ utilitários
def br(x, casas=2):
    s = f"{x:,.{casas}f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")

def pct(x, casas=1):
    return br(x * 100, casas) + "%"

UNI = ["", "um", "dois", "três", "quatro", "cinco", "seis", "sete", "oito", "nove", "dez", "onze", "doze",
       "treze", "quatorze", "quinze", "dezesseis", "dezessete", "dezoito", "dezenove"]
DEZ = ["", "", "vinte", "trinta", "quarenta", "cinquenta", "sessenta", "setenta", "oitenta", "noventa"]
CEN = ["", "cento", "duzentos", "trezentos", "quatrocentos", "quinhentos", "seiscentos", "setecentos",
       "oitocentos", "novecentos"]

def ate_mil(n):
    if n == 100:
        return "cem"
    partes = []
    c, r = divmod(n, 100)
    if c:
        partes.append(CEN[c])
    if r < 20:
        if r:
            partes.append(UNI[r])
    else:
        d, u = divmod(r, 10)
        partes.append(DEZ[d] + (f" e {UNI[u]}" if u else ""))
    return " e ".join(partes)

def extenso(valor):
    n = int(round(valor))
    mi, resto = divmod(n, 1_000_000)
    mil, uni = divmod(resto, 1000)
    partes = []
    if mi:
        partes.append(ate_mil(mi) + (" milhão" if mi == 1 else " milhões"))
    if mil:
        partes.append("mil" if mil == 1 else ate_mil(mil) + " mil")
    if uni:
        partes.append(ate_mil(uni))
    txt = partes[0]
    for p in partes[1:]:
        txt += (" e " if (p is partes[-1] and (uni < 100 or uni % 100 == 0)) else ", ") + p
    sufixo = " de reais" if (mi and not resto) else " reais"
    return txt + sufixo

# --------------------------------------------------------------- cálculos
linhas = []
for c in COMPARAVEIS:
    end, fonte, area, valor, floc, fpad, fcons, *_ = c
    unit = valor / area
    farea = (area / AVALIANDO["area"]) ** 0.125
    prod = FATOR_OFERTA * floc * farea * fpad * fcons
    linhas.append(dict(end=end, fonte=fonte, area=area, valor=valor, unit=unit, floc=floc, fpad=fpad,
                       fcons=fcons, farea=farea, prod=prod, homog=unit * prod, dorm=c[7], vagas=c[8], idade=c[9]))

h = [l["homog"] for l in linhas]
media0 = st.mean(h)
for l in linhas:
    l["desvio"] = l["homog"] / media0 - 1
    l["ok"] = abs(l["desvio"]) <= 0.30
validos = [l["homog"] for l in linhas if l["ok"]]
n = len(validos)
media = st.mean(validos)
dp = st.stdev(validos)
cv = dp / media
t = T80[n - 1]
ic_inf, ic_sup = media - t * dp / math.sqrt(n), media + t * dp / math.sqrt(n)
amplitude = (ic_sup - ic_inf) / media
valor_calc = media * AVALIANDO["area"]
arb_inf, arb_sup = valor_calc * 0.85, valor_calc * 1.15
valor_final = round(valor_calc / 1000) * 1000
fx_inf, fx_sup = ic_inf * AVALIANDO["area"], ic_sup * AVALIANDO["area"]

# graus (NBR 14653-2, tratamento por fatores)
prods_ok = all(0.80 <= l["prod"] <= 1.25 for l in linhas)
g_dados = 3 if n >= 12 else 2 if n >= 5 else 1
g_ajuste = 3 if prods_ok else 2 if all(0.50 <= l["prod"] <= 2.0 for l in linhas) else 1
itens_fund = [
    ("Caracterização do imóvel avaliando", "Completa quanto aos fatores utilizados no tratamento", 3),
    ("Quantidade mínima de dados de mercado efetivamente utilizados", f"{n} dados (Grau III exige 12; Grau II, 5)", g_dados),
    ("Identificação dos dados de mercado", "Informações de todas as características analisadas, com fotos e vistoria externa", 3),
    ("Intervalo admissível de ajuste para o conjunto de fatores",
     f"Produtos entre {br(min(l['prod'] for l in linhas),3)} e {br(max(l['prod'] for l in linhas),3)}", g_ajuste),
]
pontos = sum(i[2] for i in itens_fund)
if pontos >= 10 and g_dados == 3 and g_ajuste == 3 and min(i[2] for i in itens_fund) >= 2:
    grau_fund = "III"
elif pontos >= 6 and g_dados >= 2 and g_ajuste >= 2:
    grau_fund = "II"
else:
    grau_fund = "I"
grau_prec = "III" if amplitude <= 0.30 else "II" if amplitude <= 0.40 else "I" if amplitude <= 0.50 else "fora de enquadramento"
ROM = {1: "I", 2: "II", 3: "III"}

# ------------------------------------------------------------------ HTML
def tabela_comparaveis():
    r = ""
    for i, l in enumerate(linhas, 1):
        r += (f"<tr><td>{i}</td><td class='esq'>{l['end']}<br><span class='nota'>{l['fonte']}</span></td>"
              f"<td>{br(l['area'])}</td><td>{l['dorm']}/{l['vagas']}</td><td>{l['idade']}</td>"
              f"<td>{br(l['valor'],0)}</td><td>{br(l['unit'])}</td></tr>")
    return r

def tabela_homog():
    r = ""
    for i, l in enumerate(linhas, 1):
        r += (f"<tr><td>{i}</td><td>{br(l['unit'])}</td><td>{br(FATOR_OFERTA)}</td><td>{br(l['floc'])}</td>"
              f"<td>{br(l['farea'],3)}</td><td>{br(l['fpad'])}</td><td>{br(l['fcons'])}</td>"
              f"<td>{br(l['prod'],3)}</td><td><b>{br(l['homog'])}</b></td></tr>")
    return r

def tabela_saneamento():
    r = ""
    for i, l in enumerate(linhas, 1):
        sit = "<span class='ok'>Mantido</span>" if l["ok"] else "<span class='fora'>Descartado</span>"
        r += f"<tr><td>{i}</td><td>{br(l['homog'])}</td><td>{('+' if l['desvio']>=0 else '')}{pct(l['desvio'])}</td><td>{sit}</td></tr>"
    return r

def tabela_fund():
    r = ""
    for i, (item, desc, g) in enumerate(itens_fund, 1):
        r += f"<tr><td>{i}</td><td class='esq'>{item}</td><td class='esq'>{desc}</td><td><b>{ROM[g]}</b></td><td>{g}</td></tr>"
    return r

CSS = Path(__file__).with_name("estilo.css").read_text(encoding="utf-8")

html = f"""<!doctype html><html lang="pt-BR"><head><meta charset="utf-8">
<title>PTAM – Exemplo</title><style>{CSS}</style></head><body>

<div class="capa">
  <div class="capa-topo">
    <div class="marca"><span class="m1">SILVA</span><span class="m2">Negócios Imobiliários</span></div>
    <div class="capa-tag">Parecer nº 027/2026</div>
  </div>
  <div class="capa-meio">
    <div class="capa-tag">Avaliação mercadológica</div>
    <h1>Parecer Técnico de<br>Avaliação <span>Mercadológica</span></h1>
    <div class="sub">PTAM · Método Comparativo Direto de Dados de Mercado · ABNT NBR 14653-2</div>
    <div class="capa-dados"><table>
      <tr><td>Imóvel</td><td>{AVALIANDO['tipo']} – {AVALIANDO['area']:.0f} m² privativos</td></tr>
      <tr><td>Endereço</td><td>{AVALIANDO['endereco']}</td></tr>
      <tr><td>Matrícula</td><td>{AVALIANDO['matricula']}</td></tr>
      <tr><td>Solicitante</td><td>Maria Aparecida Souza</td></tr>
      <tr><td>Finalidade</td><td>Subsidiar a definição do preço de venda</td></tr>
      <tr><td>Data da vistoria</td><td>10/11/2026</td></tr>
    </table></div>
    <div class="capa-valor"><span>Valor de mercado</span><b>R$ {br(valor_final,2)}</b></div>
  </div>
  <div class="capa-rodape">
    <div><b>Responsável técnico:</b> João Carlos da Silva · Corretor de Imóveis · CRECI 00000-F/SC · CNAI 00000</div>
    <div>Cidade Exemplo/SC, 15 de novembro de 2026</div>
  </div>
</div>

<div class="sumario">
  <div class="titulo-pag">Sumário</div><div class="linha-laranja"></div>
  <ol>
    <li>Identificação do solicitante e do responsável técnico</li><li>Objetivo, finalidade e data de referência</li>
    <li>Documentação analisada</li><li>Vistoria e caracterização do imóvel</li>
    <li>Caracterização da região e diagnóstico de mercado</li><li>Metodologia e critérios de homogeneização</li>
    <li>Pesquisa de mercado</li><li>Tratamento dos dados por fatores</li>
    <li>Saneamento da amostra e estatística</li><li>Graus de fundamentação e de precisão</li>
    <li>Cálculo do valor e campo de arbítrio</li><li>Conclusão</li>
    <li>Pressupostos, ressalvas e limitações</li><li>Encerramento</li><li>Anexos</li>
  </ol>
  <div class="resumo">
    <div class="titulo-res">Resumo da avaliação</div>
    <div class="grid3">
      <div class="caixa"><b>Valor de mercado</b><span>R$ {br(valor_final,0)}</span></div>
      <div class="caixa"><b>Valor unitário</b><span>R$ {br(media)}/m²</span></div>
      <div class="caixa"><b>Amostra utilizada</b><span>{n} imóveis</span></div>
      <div class="caixa"><b>Faixa de negociação (IC 80%)</b><span>R$ {br(fx_inf,0)} a {br(fx_sup,0)}</span></div>
      <div class="caixa"><b>Fundamentação</b><span>Grau {grau_fund}</span></div>
      <div class="caixa"><b>Precisão</b><span>Grau {grau_prec}</span></div>
    </div>
  </div>
</div>

<section><h2><span class="n">01</span> Identificação do solicitante e do responsável técnico</h2>
<table class="dados ficha">
<tr><td>Solicitante</td><td>Maria Aparecida Souza · CPF 000.000.000-00</td></tr>
<tr><td>Condição</td><td>Proprietária do imóvel</td></tr>
<tr><td>Responsável técnico</td><td>João Carlos da Silva – Corretor de Imóveis</td></tr>
<tr><td>Registros</td><td>CRECI 00000-F/SC · CNAI 00000</td></tr>
<tr><td>Empresa</td><td>Silva Negócios Imobiliários · CRECI J-0000/SC</td></tr>
</table></section>

<section><h2><span class="n">02</span> Objetivo, finalidade e data de referência</h2>
<p>O presente parecer tem por <b>objetivo</b> determinar o <b>valor de mercado para venda</b> do imóvel descrito no item 04, entendido como a quantia mais provável pela qual se negociaria voluntária e conscientemente o bem, numa data de referência, dentro das condições do mercado vigente.</p>
<p><b>Finalidade:</b> subsidiar a proprietária na definição do preço de oferta do imóvel. <b>Data de referência:</b> 10/11/2026.</p>
</section>

<section><h2><span class="n">03</span> Documentação analisada</h2>
<table class="dados ficha">
<tr><td>Matrícula</td><td>{AVALIANDO['matricula']} – certidão de inteiro teor emitida em 03/11/2026</td></tr>
<tr><td>IPTU</td><td>{AVALIANDO['inscricao']} – exercício 2026</td></tr>
<tr><td>Convenção / condomínio</td><td>Declaração de quitação condominial fornecida pela síndica</td></tr>
<tr><td>Planta</td><td>Planta baixa da unidade, conforme projeto aprovado</td></tr>
</table>
<p class="nota">Não constam ônus reais na certidão apresentada. A análise documental limita-se aos documentos acima.</p>
</section>

<section class="quebra"><h2><span class="n">04</span> Vistoria e caracterização do imóvel</h2>
<p>Vistoria realizada em 10/11/2026, às 14h, acompanhada pela proprietária.</p>
<div class="grid2">
<table class="dados ficha">
<tr><td>Tipo</td><td>{AVALIANDO['tipo']}</td></tr>
<tr><td>Área privativa</td><td>{br(AVALIANDO['area'])} m²</td></tr>
<tr><td>Área total</td><td>95,40 m² (incluída fração de vaga e áreas comuns)</td></tr>
<tr><td>Dormitórios</td><td>{AVALIANDO['dorm']} (sendo {AVALIANDO['suites']} suíte)</td></tr>
<tr><td>Vagas de garagem</td><td>{AVALIANDO['vagas']} coberta, privativa</td></tr>
<tr><td>Pavimento</td><td>3º andar, frente, posição solar norte</td></tr>
</table>
<table class="dados ficha">
<tr><td>Idade aparente</td><td>{AVALIANDO['idade']} anos</td></tr>
<tr><td>Padrão construtivo</td><td>Normal</td></tr>
<tr><td>Conservação</td><td>Bom – necessita apenas reparos simples</td></tr>
<tr><td>Elevador</td><td>Sim (1)</td></tr>
<tr><td>Lazer</td><td>Salão de festas, playground, churrasqueira</td></tr>
<tr><td>Condomínio</td><td>R$ 520,00/mês</td></tr>
</table>
</div>
<h3>Ambientes vistoriados</h3>
<table class="dados">
<tr><th>Ambiente</th><th>Piso</th><th>Parede</th><th>Teto</th><th>Estado</th></tr>
<tr><td>Sala estar/jantar</td><td>Porcelanato</td><td>Pintura acrílica</td><td>Gesso rebaixado</td><td>Bom</td></tr>
<tr><td>Cozinha</td><td>Porcelanato</td><td>Cerâmica até o teto</td><td>Gesso</td><td>Bom</td></tr>
<tr><td>Área de serviço</td><td>Cerâmica</td><td>Cerâmica</td><td>Pintura</td><td>Bom</td></tr>
<tr><td>Suíte</td><td>Laminado</td><td>Pintura acrílica</td><td>Gesso</td><td>Bom</td></tr>
<tr><td>Dormitório 2</td><td>Laminado</td><td>Pintura acrílica</td><td>Gesso</td><td>Regular – pintura desgastada</td></tr>
<tr><td>Banheiros (2)</td><td>Porcelanato</td><td>Cerâmica</td><td>Gesso</td><td>Bom</td></tr>
<tr><td>Sacada com churrasqueira</td><td>Porcelanato</td><td>Textura</td><td>Pintura</td><td>Bom</td></tr>
</table>
<p>Imóvel em boas condições de uso e habitabilidade. Esquadrias em alumínio com vidro liso, instalações aparentes sem sinais de vazamentos ou infiltrações na inspeção visual. Recomenda-se renovação da pintura do dormitório 2, sem impacto relevante no valor.</p>
</section>

<section><h2><span class="n">05</span> Caracterização da região e diagnóstico de mercado</h2>
<p>O Bairro Jardim Primavera é predominantemente residencial, com edifícios multifamiliares de padrão normal e médio. Conta com infraestrutura completa (água, esgoto, energia, iluminação pública, pavimentação e coleta de lixo), comércio de bairro, supermercados, escolas públicas e particulares, unidade de saúde e linhas de ônibus a menos de 300 m. Está a aproximadamente 4 km do centro da cidade.</p>
<table class="dados ficha">
<tr><td>Liquidez</td><td>Média a alta – tempo médio de venda estimado entre 3 e 6 meses</td></tr>
<tr><td>Desempenho do mercado</td><td>Normal, com procura constante por unidades de 2 dormitórios</td></tr>
<tr><td>Número de ofertas</td><td>Médio – foram identificadas 23 ofertas semelhantes na região</td></tr>
<tr><td>Público-alvo</td><td>Casais e famílias pequenas, primeiro imóvel ou troca</td></tr>
<tr><td>Fatores de valorização</td><td>Posição solar norte, sacada com churrasqueira, proximidade de comércio</td></tr>
</table>
</section>

<section><h2><span class="n">06</span> Metodologia e critérios de homogeneização</h2>
<p>Foi empregado o <b>Método Comparativo Direto de Dados de Mercado</b>, previsto na ABNT NBR 14653-1 e detalhado na ABNT NBR 14653-2, que identifica o valor de mercado do bem por meio do tratamento técnico dos atributos de elementos comparáveis, constituintes de uma amostra representativa do mercado.</p>
<p>Os dados foram homogeneizados por <b>tratamento por fatores</b>, adotando-se os seguintes critérios:</p>
<table class="dados">
<tr><th>Fator</th><th>Critério adotado</th></tr>
<tr><td>Oferta</td><td class="esq">{br(FATOR_OFERTA)} – desconto de 10% sobre o preço anunciado, compatível com a margem de negociação praticada na região.</td></tr>
<tr><td>Localização</td><td class="esq">Comparação direta entre o logradouro do comparável e o do avaliando (acesso, comércio, vizinhança). Valores entre 0,95 e 1,05.</td></tr>
<tr><td>Área</td><td class="esq">F = (Área do comparável ÷ Área do avaliando)<sup>1/8</sup>, aplicável a diferenças de área inferiores a 30%.</td></tr>
<tr><td>Padrão construtivo</td><td class="esq">Ajuste de ±5% para unidades de padrão superior ou inferior ao avaliando.</td></tr>
<tr><td>Conservação</td><td class="esq">Ajuste de ±5% conforme estado de conservação observado em comparação ao avaliando.</td></tr>
</table>
<p class="nota">Parecer elaborado por corretor de imóveis nos termos da Lei nº 6.530/1978 e da Resolução COFECI nº 1.066/2007.</p>
</section>

<section><h2><span class="n">07</span> Pesquisa de mercado</h2>
<p>Foram coletados <b>{len(linhas)} elementos comparáveis</b> no mesmo bairro e em bairros vizinhos de mesma característica, entre setembro e novembro de 2026, todos apartamentos residenciais em edifícios com elevador.</p>
<table class="dados num">
<tr><th>Nº</th><th class="esq">Endereço / fonte</th><th>Área (m²)</th><th>Dorm/Vagas</th><th>Idade</th><th>Valor ofertado (R$)</th><th>R$/m²</th></tr>
{tabela_comparaveis()}
</table>
</section>

<section><h2><span class="n">08</span> Tratamento dos dados por fatores</h2>
<p>Valor unitário homogeneizado = R$/m² × F.oferta × F.localização × F.área × F.padrão × F.conservação.</p>
<table class="dados num">
<tr><th>Nº</th><th>R$/m²</th><th>F. oferta</th><th>F. local.</th><th>F. área</th><th>F. padrão</th><th>F. conserv.</th><th>Produto</th><th>R$/m² homog.</th></tr>
{tabela_homog()}
</table>
</section>

<section><h2><span class="n">09</span> Saneamento da amostra e estatística</h2>
<p>Média dos valores homogeneizados: <b>R$ {br(media0)}/m²</b>. Critério de saneamento: são mantidos os elementos cujo valor homogeneizado está no intervalo de ±30% em torno da média.</p>
<div class="grid2">
<table class="dados num">
<tr><th>Nº</th><th>R$/m² homog.</th><th>Desvio da média</th><th>Situação</th></tr>
{tabela_saneamento()}
</table>
<table class="dados ficha">
<tr><td>Elementos utilizados (n)</td><td>{n}</td></tr>
<tr><td>Média saneada</td><td>R$ {br(media)}/m²</td></tr>
<tr><td>Desvio padrão</td><td>R$ {br(dp)}/m²</td></tr>
<tr><td>Coeficiente de variação</td><td>{pct(cv)}</td></tr>
<tr><td>t de Student (80%, {n-1} g.l.)</td><td>{br(t,3)}</td></tr>
<tr><td>Limite inferior IC 80%</td><td>R$ {br(ic_inf)}/m²</td></tr>
<tr><td>Limite superior IC 80%</td><td>R$ {br(ic_sup)}/m²</td></tr>
<tr><td>Amplitude do IC 80%</td><td>{pct(amplitude)}</td></tr>
</table>
</div>
<p>Todos os elementos ficaram dentro do intervalo de saneamento. O baixo coeficiente de variação indica amostra homogênea após o tratamento.</p>
</section>

<section><h2><span class="n">10</span> Graus de fundamentação e de precisão</h2>
<h3>Fundamentação – tratamento por fatores (ABNT NBR 14653-2)</h3>
<table class="dados">
<tr><th>Item</th><th class="esq">Descrição</th><th class="esq">Situação neste parecer</th><th>Grau</th><th>Pontos</th></tr>
{tabela_fund()}
<tr><td></td><td class="esq" colspan="3"><b>Total de pontos</b></td><td><b>{pontos}</b></td></tr>
</table>
<p>Enquadramento: <b>Grau {grau_fund} de fundamentação</b>. {"Para atingir o Grau III seria necessário utilizar ao menos 12 dados de mercado." if grau_fund != "III" else ""}</p>
<h3>Precisão</h3>
<p>Amplitude do intervalo de confiança de 80% em torno do valor central: <b>{pct(amplitude)}</b>. Pela NBR 14653-2 (Grau III ≤ 30%; Grau II ≤ 40%; Grau I ≤ 50%), enquadramento em <b>Grau {grau_prec} de precisão</b>.</p>
</section>

<section><h2><span class="n">11</span> Cálculo do valor e campo de arbítrio</h2>
<div class="grid2">
<div class="caixa"><b>Valor unitário adotado (média saneada)</b><span>R$ {br(media)}/m²</span></div>
<div class="caixa"><b>Área privativa do avaliando</b><span>{br(AVALIANDO['area'])} m²</span></div>
</div>
<p style="margin-top:3mm">Valor calculado = R$ {br(media)}/m² × {br(AVALIANDO['area'])} m² = <b>R$ {br(valor_calc)}</b>.</p>
<table class="dados num">
<tr><th>Referência</th><th>Valor (R$)</th></tr>
<tr><td>Campo de arbítrio – limite inferior (−15%)</td><td>{br(arb_inf)}</td></tr>
<tr><td>Faixa de negociação – IC 80% inferior</td><td>{br(fx_inf)}</td></tr>
<tr><td><b>Valor calculado</b></td><td><b>{br(valor_calc)}</b></td></tr>
<tr><td>Faixa de negociação – IC 80% superior</td><td>{br(fx_sup)}</td></tr>
<tr><td>Campo de arbítrio – limite superior (+15%)</td><td>{br(arb_sup)}</td></tr>
</table>
<p>Não foram identificadas características do imóvel não contempladas no tratamento que justificassem afastamento do valor calculado; adota-se o valor central, arredondado conforme a tolerância de até 1% admitida pela NBR 14653-1.</p>
</section>

<section><h2><span class="n">12</span> Conclusão</h2>
<div class="destaque">
<div class="rot">Valor de mercado para venda</div>
<div class="valor">R$ {br(valor_final)}</div>
<div class="ext">({extenso(valor_final)})</div>
</div>
<div class="grid3">
<div class="caixa"><b>Data de referência</b><span>10/11/2026</span></div>
<div class="caixa"><b>Fundamentação</b><span>Grau {grau_fund}</span></div>
<div class="caixa"><b>Precisão</b><span>Grau {grau_prec}</span></div>
</div>
<p style="margin-top:3mm"><b>Recomendação ao cliente:</b> considerando a margem de negociação da região, sugere-se anunciar o imóvel entre R$ {br(round(valor_final/0.95/1000)*1000,0)} e R$ {br(round(valor_final/0.90/1000)*1000,0)}, com expectativa de fechamento próximo ao valor de mercado apurado.</p>
</section>

<section><h2><span class="n">13</span> Pressupostos, ressalvas e limitações</h2>
<ul>
<li>A documentação foi fornecida pela solicitante e considerada verdadeira; não foram realizadas pesquisas cartoriais ou judiciais além das indicadas no item 03.</li>
<li>O imóvel foi considerado livre de ônus, dívidas, ações judiciais e irregularidades, conforme certidão de matrícula apresentada.</li>
<li>As áreas consideradas são as constantes na matrícula, conferidas com a planta da unidade.</li>
<li>Não foram realizadas análises estruturais, de instalações ou ambientais; o estado de conservação refere-se à inspeção visual na data da vistoria.</li>
<li>Os dados de mercado são ofertas obtidas junto a imobiliárias, portais e corretores, e foram tratadas com fator de oferta.</li>
<li>O valor reflete as condições de mercado na data de referência e pode variar com o tempo.</li>
<li>Este parecer não substitui laudo de avaliação elaborado por engenheiro ou arquiteto quando exigido por lei, órgão público ou instituição financeira.</li>
</ul>
</section>

<section><h2><span class="n">14</span> Encerramento</h2>
<p>Nada mais havendo a esclarecer, encerra-se o presente Parecer Técnico de Avaliação Mercadológica, composto por <span class="totalpag">__</span> páginas, incluindo anexos, todas rubricadas, sendo esta datada e assinada.</p>
<p>Cidade Exemplo/SC, 15 de novembro de 2026.</p>
<div class="assinatura"><div class="traco"></div>
<b>João Carlos da Silva</b><br>Corretor de Imóveis · CRECI 00000-F/SC · CNAI 00000</div>
</section>

<section class="quebra"><h2><span class="n">15</span> Anexos</h2>
<h3>A. Relatório fotográfico</h3>
<div class="fotos"><div class="foto">Fachada do edifício</div><div class="foto">Sala estar/jantar</div>
<div class="foto">Cozinha</div><div class="foto">Suíte</div><div class="foto">Banheiro social</div><div class="foto">Sacada com churrasqueira</div></div>
<h3 style="margin-top:5mm">B. Mapa de localização do imóvel e dos comparáveis</h3>
<div class="foto" style="height:62mm">Mapa com o avaliando e os {len(linhas)} comparáveis</div>
<h3 style="margin-top:5mm">C. Documentos anexos</h3>
<ul><li>Certidão de inteiro teor da matrícula nº 45.678</li><li>Carnê de IPTU 2026</li><li>Fichas e anúncios dos {len(linhas)} elementos comparáveis</li><li>Declaração de quitação condominial</li></ul>
</section>
</body></html>"""

Path(__file__).with_name("relatorio-ptam-exemplo.html").write_text(html, encoding="utf-8")
print(f"valor_final={valor_final} media={media:.2f} cv={cv:.4f} amp={amplitude:.4f} fund={grau_fund} prec={grau_prec} pontos={pontos}")
print(extenso(valor_final))
