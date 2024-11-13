from django.shortcuts import render
from django.http import HttpResponse
import sidrapy
import pandas as pd
import io

def index(request):
    return render(request, 'template.html')  # Nome do template HTML

def mostrar_dados(request):
    # Obtém o ano escolhido pelo usuário através do formulário
    ano_escolhido = request.GET.get('ano')

    # Se o ano não foi selecionado, redireciona para a página inicial
    if not ano_escolhido:
        return render(request, 'template.html', {"error": "Por favor, selecione um ano."})

    # Extrai os dados do SIDRA, filtrando pelo ano escolhido
    data = sidrapy.get_table(
        table_code="992",
        territorial_level="3",
        ibge_territorial_code="all",
        classifications={"12762": "117839,117844", "319": "104029", "2703": "117933"},
        period=ano_escolhido,  # Usa o ano escolhido pelo usuário
        format="pandas"
    )

    # Renomeia e filtra as colunas desejadas
    data = data.rename(columns={
        "D1N": "sigla_estado",
        "D2N": "ano",
        "D3N": "classificacao_atividade",
        "D4N": "variavel",
        "V": "quantidade"
    })
    data = data[['classificacao_atividade', 'ano', 'sigla_estado', 'variavel', 'quantidade']]

    # Converte os dados para uma lista de dicionários para facilitar a exibição no template
    dados_por_ano = data.to_dict('records')

    return render(request, 'mostrar_dados.html', {
        'dados': dados_por_ano,
        'ano_escolhido': ano_escolhido
    })

def download_dados(request):
    try:
        # Obtém o ano escolhido pelo usuário para o download
        ano_escolhido = request.GET.get('ano')

        # Extrai os dados do SIDRA, filtrando pelo ano escolhido
        data = sidrapy.get_table(
            table_code="992",
            territorial_level="3",
            ibge_territorial_code="all",
            classifications={"12762": "117839,117844", "319": "104029", "2703": "117933"},
            period=ano_escolhido,  # Usa o ano escolhido pelo usuário
            format="pandas"
        )

        # Renomeia e filtra as colunas desejadas
        data = data.rename(columns={
            "D1N": "sigla_estado",
            "D2N": "ano",
            "D3N": "classificacao_atividade",
            "D4N": "variavel",
            "V": "quantidade"
        })
        data = data[['classificacao_atividade', 'ano', 'sigla_estado', 'variavel', 'quantidade']]

        # Gera o arquivo Excel
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            data.to_excel(writer, index=False)
        buffer.seek(0)

        # Configura a resposta HTTP para download
        response = HttpResponse(buffer, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = f'attachment; filename="dados_sidra_{ano_escolhido}.xlsx"'
        return response

    except Exception as e:
        # Retorna uma resposta de erro com a mensagem da exceção
        return HttpResponse(f"Ocorreu um erro: {e}", status=500)
