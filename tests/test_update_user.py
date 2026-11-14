import allure
import pytest
import requests

from urls import LOGIN_URL, USER_URL


class TestUpdateUser:

    @allure.title('Изменение данных с авторизацией')
    @pytest.mark.parametrize('field', ['email', 'name', 'password'])
    def test_update_user_with_authorization_returns_updated_data(
        self, registered_user, field
    ):
        user = registered_user['data']
        new_values = {
            'email': f"updated_{user['email']}",
            'name': 'Updated User',
            'password': 'UpdatedPassword456!',
        }
        payload = {field: new_values[field]}
        expected_user = user.copy()
        expected_user.update(payload)

        response = requests.patch(
            USER_URL,
            headers={'Authorization': registered_user['token']},
            json=payload,
            timeout=30,
        )

        login_response = requests.post(
            LOGIN_URL,
            json={
                'email': expected_user['email'],
                'password': expected_user['password'],
            },
            timeout=30,
        )

        assert response.status_code == 200
        assert response.json() == {
            'success': True,
            'user': {
                'email': expected_user['email'],
                'name': expected_user['name'],
            },
        }

        assert login_response.status_code == 200
        assert login_response.json()['success'] is True
        assert login_response.json()['user'] == {
            'email': expected_user['email'],
            'name': expected_user['name'],
        }

    @allure.title('Изменение данных без авторизации')
    @pytest.mark.parametrize('field', ['email', 'name', 'password'])
    def test_update_user_without_authorization_returns_error(
        self, registered_user, field
    ):
        user = registered_user['data']
        new_values = {
            'email': f"updated_{user['email']}",
            'name': 'Updated User',
            'password': 'UpdatedPassword456!',
        }

        response = requests.patch(
            USER_URL,
            json={field: new_values[field]},
            timeout=30,
        )

        assert response.status_code == 401
        assert response.json() == {
            'success': False,
            'message': 'You should be authorised',
        }