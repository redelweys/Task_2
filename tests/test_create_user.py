import allure
import requests
import pytest

from urls import REGISTER_URL


class TestCreateUser:

    @allure.title('Создание уникального пользователя')
    def test_create_unique_user_returns_success(
        self, user_data, user_cleanup
    ):
        response = requests.post(
            REGISTER_URL,
            json=user_data,
            timeout=30,
        )
        body = response.json()

        token = body.get('accessToken')
        if token:
            user_cleanup.append(token)

        assert response.status_code == 200
        assert body['success'] is True
        assert body['user'] == {
            'email': user_data['email'],
            'name': user_data['name'],
        }
        assert isinstance(token, str) and token.startswith('Bearer ')
        assert isinstance(body.get('refreshToken'), str) and body['refreshToken']
        
    @allure.title('Повторная регистрация пользователя')
    def test_create_existing_user_returns_error(
        self, user_data, user_cleanup
    ):
        first_response = requests.post(
            REGISTER_URL,
            json=user_data,
            timeout=30,
        )
        first_body = first_response.json()

        token = first_body.get('accessToken')
        if token:
            user_cleanup.append(token)

        assert first_response.status_code == 200
        assert first_body['success'] is True

        response = requests.post(
            REGISTER_URL,
            json=user_data,
            timeout=30,
        )

        assert response.status_code == 403
        assert response.json() == {
            'success': False,
            'message': 'User already exists',
        }

    @allure.title('Регистрация без обязательного поля')
    @pytest.mark.parametrize('missing_field', [
        'email',
        'password',
        'name',
    ])
    def test_create_user_without_required_field_returns_error(
        self, user_data, user_cleanup, missing_field
    ):
        payload = user_data.copy()
        del payload[missing_field]

        response = requests.post(
            REGISTER_URL,
            json=payload,
            timeout=30,
        )
        body = response.json()

        token = body.get('accessToken')
        if token:
            user_cleanup.append(token)

        assert response.status_code == 403
        assert body == {
            'success': False,
            'message': 'Email, password and name are required fields',
        }