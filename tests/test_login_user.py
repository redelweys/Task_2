import allure
import pytest
import requests

from urls import LOGIN_URL


class TestLoginUser:

    @allure.title('Вход зарегистрированного пользователя')
    def test_login_existing_user_returns_success(self, registered_user):
        user = registered_user['data']
        payload = {
            'email': user['email'],
            'password': user['password'],
        }

        response = requests.post(
            LOGIN_URL,
            json=payload,
            timeout=30,
        )
        body = response.json()

        assert response.status_code == 200
        assert body['success'] is True
        assert body['user'] == {
            'email': user['email'],
            'name': user['name'],
        }
        assert isinstance(body.get('accessToken'), str)
        assert body['accessToken'].startswith('Bearer ')
        assert isinstance(body.get('refreshToken'), str)
        assert body['refreshToken']

    @allure.title('Вход с неверными учётными данными')
    @pytest.mark.parametrize('wrong_field', ['email', 'password'])
    def test_login_with_wrong_credentials_returns_error(
        self, registered_user, wrong_field
    ):
        user = registered_user['data']
        payload = {
            'email': user['email'],
            'password': user['password'],
        }
        if wrong_field == 'email':
            payload['email'] = f"wrong_{user['email']}"
        else:
            payload['password'] = 'WrongPassword456!'

        response = requests.post(
            LOGIN_URL,
            json=payload,
            timeout=30,
        )

        assert response.status_code == 401
        assert response.json() == {
            'success': False,
            'message': 'email or password are incorrect',
        }