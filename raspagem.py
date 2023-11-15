import instaloader
import csv
import time
from random import randint

# Lista de credenciais (usuário, senha)
credenciais = [
    ('instagram_user', 'instagram_senha'),

    # Adicione mais contas conforme necessário
]

# Define o nome de usuário do perfil
username = "perfil_para_raspagem"

# Índice para acompanhar qual conta está sendo usada
indice_conta = 0

# Cria uma instância do Instaloader
L = instaloader.Instaloader()

# Loop infinito
while True:
    # Tenta fazer login com cada conta até conseguir ou exaurir a lista
    while True:
        try:
            usuario_atual, senha_atual = credenciais[indice_conta]
            L.login(usuario_atual, senha_atual)
            break  # Sai do loop se o login for bem-sucedido
        except instaloader.exceptions.InstaloaderException as e:
            print(f"Erro de login para a conta {usuario_atual}: {e}")
            indice_conta = (indice_conta + 1) % len(credenciais)
            if indice_conta == 0:
                raise  # Levanta uma exceção se todas as contas falharem

    # Carrega o perfil
    profile = instaloader.Profile.from_username(L.context, username)

    # Tenta ler os shortcodes já processados
    try:
        with open('shortcodes_processados.txt', 'r') as f:
            shortcodes_processados = set(f.read().strip().split('\n'))
    except FileNotFoundError:
        shortcodes_processados = set()

    # Conjunto para armazenar os comentários únicos já processados
    comentarios_processados = set()

    # Contador para limitar a quantidade de posts processados
    count = 0

    # Loop através dos posts do perfil
    for post in profile.get_posts():
        # Pula posts já processados
        if post.shortcode in shortcodes_processados:
            continue

        # Verifica se já processou 5 posts
        if count >= 10:
            break

        # Abre o arquivo CSV para adicionar dados
        with open('comentarios.csv', 'a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            for comment in post.get_comments():
                comentario_id = (post.shortcode, comment.owner.username, comment.created_at_utc)
                if comentario_id not in comentarios_processados:
                    writer.writerow([post.shortcode, comment.owner.username, comment.created_at_utc, comment.text])
                    comentarios_processados.add(comentario_id)

        # Salva o shortcode como processado
        shortcodes_processados.add(post.shortcode)

        # Espera um intervalo aleatório entre 1 e 10 segundos antes de processar o próximo post
        time.sleep(randint(1, 10))

        # Incrementa o contador
        count += 1

    # Salva os shortcodes processados
    with open('shortcodes_processados.txt', 'w') as f:
        f.write('\n'.join(shortcodes_processados))

    # Atualiza o índice da conta para a próxima iteração
    indice_conta = (indice_conta + 1) % len(credenciais)

    # Espera um intervalo aleatório entre 1 e 60 segundos antes da próxima iteração do loop
    time.sleep(randint(30, 60))
