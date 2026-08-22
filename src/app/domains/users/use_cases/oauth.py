


class OAuthService:
    def login_google(
        self,
        google_token: str,
    ) -> dict:
        """
        Login via Google.

        A validação do token do Google ainda precisa ser implementada.

        O ideal é criar um GoogleAuthService separado para:
        1. validar o token;
        2. obter email/nome/google_id;
        3. localizar ou criar o usuário;
        4. retornar os tokens da aplicação.
        """

        raise NotImplementedError(
            "Integração com Google ainda não implementada"
        )

