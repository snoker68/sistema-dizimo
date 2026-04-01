# 💒 Sistema de Controle de Dízimo v1.3.6

Bem-vindo ao repositório do Sistema de Dízimo! Este projeto foi desenvolvido para facilitar a gestão financeira e o cadastro de fiéis em comunidades religiosas.

---

## 📚 Documentação e Estudo

Preparamos materiais especiais para você:

1.  **[Manual Profissional do Usuário](DOCUMENTACAO_PROFISSIONAL.md)** 📖
    - Guia completo de como usar o sistema (Login, Cadastros, Dashboard e Excel).
2.  **[Tutorial de Desenvolvimento Passo a Passo](TUTORIAL_DESENVOLVIMENTO.md)** 💻
    - Criado para quem quer aprender a construir este sistema do zero (Modelagem, Views, Front-end e DevOps).

---

## ⚡ Como rodar este projeto localmente
Se você quiser rodar na sua máquina, siga estes passos:
1.  Crie um ambiente virtual: `python -m venv venv`
2.  Instale as dependências: `pip install -r requirements.txt`
3.  Rode as migrações: `python manage.py migrate`
4.  Crie um superusuário: `python manage.py createsuperuser`
5.  Inicie o servidor: `python manage.py runserver`

## 🚀 Deploy e Automação
O sistema está configurado com **GitHub Webhooks** para atualizar automaticamente no **PythonAnywhere** a cada `git push`.

---
*Que este sistema seja uma benção para a sua comunidade!* ✨ Church ⛪
