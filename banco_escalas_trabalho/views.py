from django.shortcuts import render, redirect
from django.http import HttpResponse
import mysql.connector
from datetime import datetime, timedelta
from django.core.paginator import Paginator

def conexao():

        return mysql.connector.connect(
            host='54.167.2.150',
            user='host',
            password='batata',
            database='escalas'
        )



def home_view(request):
    # Conectando ao banco de dados
    conn = conexao()

    # Criando o cursor
    cursor = conn.cursor()

    # Pegando os filtros da solicitação
    nome_pesquisa = request.GET.get('nome', '').strip()
    data_filtro = request.GET.get('data', '').strip()
    semana_filtro = request.GET.get('semana', '').strip()
    cargo_filtro = request.GET.get('cargo', '').strip()
    turno_filtro = request.GET.get('turno', '').strip()
    departamento_filtro = request.GET.get('departamento', '').strip()

    # Convertendo data_filtro para o formato de data se não estiver vazio
    if data_filtro:
        try:
            data_filtro = datetime.strptime(data_filtro, '%Y-%m-%d').date()
        except ValueError:
            # Se a data não estiver no formato correto, ignore o filtro
            data_filtro = None

    # Montando a query dinâmica com base nos filtros
    query = """
        SELECT 
            funcionarios.id,
            funcionarios.nome,
            cargos.cargo,
            turnos.tipo,
            escalas.data,
            escalas.observacao
        FROM 
            funcionarios
        JOIN 
            cargos ON funcionarios.cargo_id = cargos.id
        JOIN 
            escalas ON funcionarios.id = escalas.funcionario_id
        JOIN 
            turnos ON escalas.turno_id = turnos.id
        JOIN 
            departamentos ON cargos.departamento_id = departamentos.id
        WHERE 1=1
    """

    params = []

    if nome_pesquisa:
        query += " AND funcionarios.nome LIKE %s"
        params.append(f"%{nome_pesquisa}%")
    if data_filtro:
        query += " AND escalas.data = %s"
        params.append(data_filtro)
    if semana_filtro:
        query += " AND escalas.semana_id = %s"
        params.append(semana_filtro)
    if cargo_filtro:
        query += " AND cargos.cargo = %s"
        params.append(cargo_filtro)
    if turno_filtro:
        query += " AND turnos.tipo = %s"
        params.append(turno_filtro)
    if departamento_filtro:
        query += " AND departamentos.departamento = %s"
        params.append(departamento_filtro)

    query += " ORDER BY escalas.data ASC"
    cursor.execute(query, params)
    dados_funcionarios = cursor.fetchall()

    # Consultando dados distintos para os filtros
    cursor.execute("SELECT DISTINCT data FROM escalas ORDER BY data")
    datas = [data[0] for data in cursor.fetchall()]

    cursor.execute("""
        SELECT DISTINCT semanas.id, semanas.data_inicio, semanas.data_fim 
        FROM semanas
        LEFT JOIN escalas ON semanas.id = escalas.semana_id
        ORDER BY semanas.data_inicio
    """)
    semanas = [{"id": semana[0], "inicio": semana[1], "fim": semana[2]} for semana in cursor.fetchall()]


    cursor.execute("SELECT DISTINCT cargos.cargo FROM cargos")
    cargos = [cargo[0] for cargo in cursor.fetchall()]

    cursor.execute("SELECT DISTINCT turnos.tipo FROM turnos")
    turnos = [turno[0] for turno in cursor.fetchall()]

    cursor.execute("SELECT DISTINCT departamentos.departamento FROM departamentos")
    departamentos = [departamento[0] for departamento in cursor.fetchall()]

    # Fechando o cursor e a conexão
    cursor.close()
    conn.close()

    # Paginação - Definindo o número de itens por página
    paginator = Paginator(dados_funcionarios, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Passando os dados paginados e de filtro para o template
    return render(request, 'template_home.html', {
        'dados_funcionarios': page_obj,
        'datas': datas,
        'semanas': semanas,
        'cargos': cargos,
        'turnos': turnos,
        'departamentos': departamentos,
        'nome_pesquisa': nome_pesquisa,
        'data_filtro': data_filtro,
        'semana_filtro': semana_filtro,
        'cargo_filtro': cargo_filtro,
        'turno_filtro': turno_filtro,
        'departamento_filtro': departamento_filtro
    })



def cadastrar_departamento_view(request):
    if request.method == "POST":
        nome_departamento = request.POST.get("nome_departamento")
        if nome_departamento:
            conn = conexao()
            cursor = conn.cursor()

            # Inserindo o departamento no banco
            cursor.execute("INSERT INTO departamentos (departamento) VALUES (%s)", (nome_departamento,))
            conn.commit()
            cursor.close()
            conn.close()

            # Redirecionando para o template_home.html
            return redirect('template_home')
    return render(request, 'cadastrar_departamento.html')

def cadastrar_cargo_view(request):
    conn = conexao()
    cursor = conn.cursor(dictionary=True)

    if request.method == "POST":
        cargo = request.POST.get("cargo")
        departamento_id = request.POST.get("departamento_id")
        carga_horaria = request.POST.get("carga_horaria")

        query = """
        INSERT INTO cargos (cargo, departamento_id, carga_horaria)
        VALUES (%s, %s, %s)
        """
        cursor.execute(query, (cargo, departamento_id, carga_horaria))
        conn.commit()

        cursor.close()
        conn.close()

        return redirect("template_home")

    # Obter os departamentos para exibir no formulário
    cursor.execute("SELECT id, departamento FROM departamentos")
    departamentos = cursor.fetchall()

    cursor.close()
    conn.close()

    return render(request, "cadastrar_cargo.html", {"departamentos": departamentos})

def visualizar_funcionario_view(request, id):
    conn = conexao()
    cursor = conn.cursor()

    # Consulta para obter as informações do funcionário
    query_funcionario = """
    SELECT funcionarios.nome, cargos.cargo, departamentos.departamento
    FROM funcionarios
    JOIN cargos ON funcionarios.cargo_id = cargos.id
    JOIN departamentos ON cargos.departamento_id = departamentos.id
    WHERE funcionarios.id = %s

    """
    cursor.execute(query_funcionario, (id,))
    funcionario = cursor.fetchone()

    if not funcionario:
        return HttpResponse("Erro: Funcionário não encontrado", status=404)

    # Consulta para obter as escalas do funcionário
    query_escalas = """
    SELECT escalas.data, turnos.tipo, escalas.observacao
    FROM escalas
    JOIN turnos ON escalas.turno_id = turnos.id
    WHERE escalas.funcionario_id = %s
    """
    cursor.execute(query_escalas, (id,))
    escalas = cursor.fetchall()

    cursor.close()
    conn.close()

    return render(request, 'visualizar_funcionario.html', {
        'funcionario': funcionario,
        'escalas': escalas
    })

def cadastrar_funcionario_view(request):
    if request.method == 'POST':
        nome = request.POST.get('nome')
        cargo_id = request.POST.get('cargo_id')

        if nome and cargo_id:
            conn = conexao()
            cursor = conn.cursor(dictionary=True)

            # Inserindo o novo funcionário no banco de dados
            query = "INSERT INTO funcionarios (nome, cargo_id) VALUES (%s, %s)"
            cursor.execute(query, (nome, cargo_id))
            conn.commit()

            cursor.close()
            conn.close()

            # Redirecionando para a página de sucesso ou listagem de funcionários
            return redirect('template_home')

        else:
            return HttpResponse("Por favor, preencha todos os campos.", status=400)

    # Obter todos os cargos para exibir no formulário
    conn = conexao()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, cargo FROM cargos")
    cargos = cursor.fetchall()
    cursor.close()
    conn.close()

    return render(request, 'cadastrar_funcionario.html', {'cargos': cargos})

def visualizar_adicionar_semanas_view(request):
    conn = conexao()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM semanas ORDER BY data_inicio ASC")
    semanas = cursor.fetchall()

    data_atual = datetime.now()

    # Verificar a última semana e adicionar semanas se necessário
    if semanas:
        ultima_semana = datetime.combine(semanas[-1]['data_fim'], datetime.min.time())
        proxima_semana_inicio = ultima_semana + timedelta(days=1)
    else:
        proxima_semana_inicio = datetime(data_atual.year, 1, 1)

    # Adicionar semanas até a data atual
    while proxima_semana_inicio <= data_atual:
        proxima_semana_fim = proxima_semana_inicio + timedelta(days=6)
        cursor.execute("INSERT INTO semanas (data_inicio, data_fim) VALUES (%s, %s)",
                       (proxima_semana_inicio, proxima_semana_fim))
        conn.commit()
        proxima_semana_inicio = proxima_semana_fim + timedelta(days=1)

    # Adicionar uma nova semana ao receber uma requisição POST
    if request.method == 'POST':
        proxima_semana_fim = proxima_semana_inicio + timedelta(days=6)
        cursor.execute("INSERT INTO semanas (data_inicio, data_fim) VALUES (%s, %s)",
                       (proxima_semana_inicio, proxima_semana_fim))
        conn.commit()
        return redirect('visualizar_adicionar_semanas')

    cursor.close()
    conn.close()

    return render(request, 'visualizar_adicionar_semanas.html', {
        'semanas': semanas,
        'data_atual': data_atual
    })


from datetime import timedelta

def cadastrar_escala_view(request):
    if request.method == 'GET':
        # Recuperar funcionários
        conn = conexao()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT f.id, f.nome
            FROM funcionarios f
        """)
        funcionarios = cursor.fetchall()
        cursor.close()

        # Recuperar semanas
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT s.id, s.data_inicio, s.data_fim
            FROM semanas s
            ORDER BY s.data_inicio
        """)
        semanas = cursor.fetchall()
        cursor.close()
        conn.close()

        # Definir os dias da semana
        dias_semana = [
            {"nome": "Segunda-feira", "key": "segunda"},
            {"nome": "Terça-feira", "key": "terca"},
            {"nome": "Quarta-feira", "key": "quarta"},
            {"nome": "Quinta-feira", "key": "quinta"},
            {"nome": "Sexta-feira", "key": "sexta"},
            {"nome": "Sábado", "key": "sabado"},
            {"nome": "Domingo", "key": "domingo"},
        ]

        context = {
            'funcionarios': funcionarios,
            'semanas': semanas,
            'dias_semana': dias_semana,
        }

        return render(request, 'cadastrar_escala.html', context)

    elif request.method == 'POST':
        funcionario_id = request.POST.get('funcionario')
        semana_id = request.POST.get('semana')

        # Recuperar a data de início da semana selecionada
        conn = conexao()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT data_inicio
            FROM semanas
            WHERE id = %s
        """, [semana_id])
        resultado = cursor.fetchall()
        semana_inicio = resultado[0]['data_inicio'] if resultado else None
        cursor.close()

        # Adicionar escala para cada dia da semana
        if semana_inicio:
            dias_semana = ["segunda", "terca", "quarta", "quinta", "sexta", "sabado", "domingo"]
            for i, dia_key in enumerate(dias_semana):
                turno_tipo = request.POST.get(dia_key)
                observacao = request.POST.get(f"{dia_key}_observacao", '')

                # Inserir o turno, incluindo "não_trabalha", como qualquer outro
                cursor = conn.cursor(dictionary=True)
                cursor.execute("""
                    SELECT id
                    FROM turnos
                    WHERE tipo = %s
                """, [turno_tipo])
                resultado_turno = cursor.fetchall()
                turno_id = resultado_turno[0]['id'] if resultado_turno else None
                cursor.close()

                if turno_id is not None:
                    # Calcular a data do dia
                    data_dia = semana_inicio + timedelta(days=i)

                    # Inserir escala
                    cursor = conn.cursor()
                    cursor.execute("""
                        INSERT INTO escalas (semana_id, funcionario_id, turno_id, data, observacao)
                        VALUES (%s, %s, %s, %s, %s)
                    """, [semana_id, funcionario_id, turno_id, data_dia, observacao])
                    conn.commit()
                    cursor.close()

        conn.close()
        return redirect('template_home')
    

def excluir_escala_view(request):
    if request.method == 'POST':
        # Recuperando o ID da escala a ser excluída do formulário
        escala_id = request.POST.get('escala_id')

        # Conectando ao banco de dados
        conn = conexao()
        cursor = conn.cursor()

        # Deletando a escala com o ID fornecido
        cursor.execute("""
            DELETE FROM escalas
            WHERE id = %s
        """, [escala_id])

        conn.commit()
        cursor.close()
        conn.close()

        # Redirecionando após exclusão
        return redirect('template_home')

    else:
        # Conectando ao banco de dados
        conn = conexao()
        cursor = conn.cursor()

        # Consultando os funcionários com informações de cargo, turno, data e observações
        cursor.execute("""
            SELECT 
                funcionarios.id,
                funcionarios.nome,
                cargos.cargo,
                turnos.tipo,
                escalas.data,
                escalas.observacao,
                escalas.id AS escala_id
            FROM 
                funcionarios
            JOIN 
                cargos ON funcionarios.cargo_id = cargos.id
            JOIN 
                escalas ON funcionarios.id = escalas.funcionario_id
            JOIN 
                turnos ON escalas.turno_id = turnos.id
        """)
        dados_funcionarios = cursor.fetchall()

        # Fechando o cursor e a conexão
        cursor.close()
        conn.close()
        # Paginação - Definindo o número de itens por página
        paginator = Paginator(dados_funcionarios, 10)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        # Passando os dados para o template
        return render(request, 'excluir_escala.html', {
            'dados_funcionarios': page_obj
        })