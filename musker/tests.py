from django.contrib.auth.models import User
from django.contrib.messages import get_messages
from django.shortcuts import get_object_or_404
from django.test import TestCase, Client
from django.urls import reverse

from musker.models import Meep


class IndexViewTestCase(TestCase):

    def test_home_view(self):
        path = reverse('home')
        response = self.client.get(path)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home.html')

    def test_edit_profile(self):
        path = reverse('edit_profile')
        response = self.client.get(path)

        self.assertEqual(response.status_code, 302)

        user = User.objects.create_user(username='testuser', password='testpassword')
        self.client.login(username='testuser', password='testpassword')
        path = reverse('edit_profile')
        response = self.client.get(path)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'edit_profile.html')

    def test_add_meep(self):
        path = reverse('add_meeps')
        response = self.client.get(path)

        self.assertEqual(response.status_code, 302)

        user = User.objects.create_user(username='testuser', password='testpassword')
        self.client.login(username='testuser', password='testpassword')
        path = reverse('add_meeps')
        response = self.client.get(path)
        meep = Meep.objects.create(user=user, body='test')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context_data['title'], 'Add Meep')
        self.assertEqual(Meep.objects.all().count(), 1)
        self.assertEqual(Meep.objects.first().body, 'test')
        self.assertEqual(Meep.objects.first().user_id, 1)

    def test_profile_list(self):
        path = reverse('profile_list')
        response = self.client.get(path)

        self.assertEqual(response.status_code, 302)

        user = User.objects.create_user(username='testuser', password='testpassword')
        self.client.login(username='testuser', password='testpassword')
        path = reverse('profile_list')
        response = self.client.get(path)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'profile_list.html')

    def test_login(self):
        path = reverse('login')
        response = self.client.get(path)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'login_form.html')


class MeepDeleteTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.meep = Meep.objects.create(user=self.user, body='Test Meep')

    def test_delete_meep(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(reverse('delete_meep', args=[self.meep.pk]))
        self.assertEqual(response.status_code, 302) # Проверяем, что получаем перенаправление
        self.assertEqual(Meep.objects.filter(id=self.meep.pk).exists(), False) # Проверяем, что объект Meep был удален
        messages = [m.message for m in get_messages(response.wsgi_request)]
        self.assertIn("Meep deleted successfully.", messages) # Проверяем, что выводится соответствующее сообщение об успешном удалении

    def test_delete_nonexistent_meep(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(reverse('delete_meep', args=[100])) # Пытаемся удалить несуществующий объект Meep
        self.assertEqual(response.status_code, 404) # Проверяем, что получаем 404
        # self.assertContains(response, "That Meep Does Not Exist...") # Проверяем, что выводится соответствующее сообщение об ошибке

    def test_unauthenticated_delete_meep(self):
        response = self.client.get(reverse('delete_meep', args=[self.meep.pk]))
        self.assertEqual(response.status_code, 302)  # Проверяем, что получаем перенаправление
        self.assertEqual(Meep.objects.filter(id=self.meep.pk).exists(), True)  # Проверяем, что объект Meep не был удален

    def test_delete_other_user_meep(self):
        other_user = User.objects.create_user(username='otheruser', password='testpassword')
        self.client.login(username='otheruser', password='testpassword')
        response = self.client.post(
            reverse('delete_meep', args=[self.meep.pk]))  # Пытаемся удалить Meep другого пользователя
        self.assertEqual(response.status_code, 302)  # Проверяем, что получаем перенаправление
        self.assertTrue(Meep.objects.filter(id=self.meep.pk).exists())  # Проверяем, что объект Meep не был удален
        messages = [m.message for m in get_messages(response.wsgi_request)]
        self.assertIn("You are trying to delete someone else's Meep.",
                      messages)  # Проверяем, что выводится соответствующее сообщение об ошибке


class MeepLikeTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.meep = Meep.objects.create(user=self.user, body='Test meep')

    def test_meep_like_add(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.post(reverse('meep_like', args=[self.meep.pk]))
        self.assertEqual(response.status_code, 302)  # Check if redirecting
        self.meep.refresh_from_db()
        self.assertTrue(self.meep.likes.filter(id=self.user.id).exists())

    def test_meep_like_remove(self):
        self.meep.likes.add(self.user)
        self.client.login(username='testuser', password='testpassword')
        response = self.client.post(reverse('meep_like', args=[self.meep.pk]))
        self.assertEqual(response.status_code, 302)  # Check if redirecting
        self.meep.refresh_from_db()
        self.assertFalse(self.meep.likes.filter(id=self.user.id).exists())

    def test_meep_like_unauthenticated(self):
        response = self.client.post(reverse('meep_like', args=[self.meep.pk]))
        self.assertEqual(response.status_code, 302)  # Check if redirecting
        # self.assertRedirects(response, '/accounts/login/?next=/meeps/')  # Check if redirected to login page

    def test_meep_like_invalid_pk(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.post(reverse('meep_like', args=[999]))
        self.assertEqual(response.status_code, 404)  # Check if not found

    def test_meep_like_referer(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.post(reverse('meep_like', args=[self.meep.pk]), HTTP_REFERER='/meeps/')
        self.assertEqual(response.status_code, 302)  # Check if redirecting
        # self.assertRedirects(response, '/meeps/')  # Check if redirected to referer URL


class MeepLikeTestCase2(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.meep = Meep.objects.create(user_id=1, body='Test meep')

    def test_meep_like(self):
        # Создаем URL для функции meep_like с pk=1
        url = reverse('meep_like', kwargs={'pk': 1})

        # Авторизуемся как пользователь
        self.client.force_login(self.user)

        # Отправляем POST запрос на URL
        response = self.client.post(url)

        # Проверяем, что статус код ответа равен 302 (перенаправление)
        self.assertEqual(response.status_code, 302)

        # Получаем обновленный объект Meep из базы данных
        updated_meep = get_object_or_404(Meep, id=self.meep.id)

        # Проверяем, что пользователь добавлен в список лайков Meep
        self.assertTrue(updated_meep.likes.filter(id=self.user.id).exists())

        # Отправляем еще один POST запрос на URL
        response = self.client.post(url)

        # Проверяем, что статус код ответа равен 302 (перенаправление)
        self.assertEqual(response.status_code, 302)

        # Получаем обновленный объект Meep из базы данных
        updated_meep = get_object_or_404(Meep, id=self.meep.id)

        # Проверяем, что пользователь удален из списка лайков Meep
        self.assertFalse(updated_meep.likes.filter(id=self.user.id).exists())

class MeepEditTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.meep = Meep.objects.create(user=self.user, body='Test Meep')

    def test_edit_meep(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.post(reverse('edit_meep', args=[self.meep.pk]),
                                    {'body': 'Updated Meep'})  # Отправляем POST-запрос с обновленным текстом Meep
        self.assertEqual(response.status_code, 302)  # Проверяем, что получаем перенаправление
        self.meep.refresh_from_db()  # Обновляем объект Meep из базы данных
        self.assertEqual(self.meep.body, 'Updated Meep')  # Проверяем, что текст Meep был обновлен
        messages = [m.message for m in get_messages(response.wsgi_request)]
        self.assertIn("Your Meep Has Been Updated!",
                      messages)  # Проверяем, что выводится соответствующее сообщение об успешном обновлении

    def test_edit_other_user_meep(self):
        other_user = User.objects.create_user(username='otheruser', password='testpassword')
        self.client.login(username='otheruser', password='testpassword')
        response = self.client.post(reverse('edit_meep', args=[self.meep.pk]),
                                    {'body': 'Updated Meep'})  # Пытаемся обновить Meep другого пользователя
        self.assertEqual(response.status_code, 302)  # Проверяем, что получаем перенаправление
        self.meep.refresh_from_db()  # Обновляем объект Meep из базы данных
        self.assertNotEqual(self.meep.body, 'Updated Meep')  # Проверяем, что текст Meep не был обновлен
        messages = [m.message for m in get_messages(response.wsgi_request)]
        self.assertIn("You do not have access rights",
                      messages)  # Проверяем, что выводится соответствующее сообщение об ошибке


class AuthorizationTest(TestCase):
    def test_authorization(self):
        # Создаем пользователя
        user = User.objects.create_user(username='testuser', password='testpassword')

        # Проверяем, что пользователь не авторизован
        self.assertFalse(self.client.login(username='testuser', password='wrongpassword'))

        # Проверяем, что пользователь успешно авторизован
        self.assertTrue(self.client.login(username='testuser', password='testpassword'))

    def test_admin_authorization(self):
        # Создаем суперпользователя
        superuser = User.objects.create_superuser(username='admin', password='adminpassword')

        # Проверяем, что суперпользователь успешно авторизован
        self.assertTrue(self.client.login(username='admin', password='adminpassword'))


class UserRegistrationTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.registration_url = reverse('registration')
        self.home_url = reverse('home')
        self.user_data = {
            'username': 'testuser',
            'password1': 'testpassword',
            'password2': 'testpassword',
        }

    def test_user_registration_success(self):
        response = self.client.post(self.registration_url, data=self.user_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.home_url)

        user = User.objects.get(username=self.user_data['username'])
        self.assertEqual(user.username, self.user_data['username'])
        # Дополнительные проверки, если необходимо

    def test_user_registration_invalid_form(self):
        invalid_data = self.user_data.copy()
        invalid_data['password2'] = 'differentpassword'

        response = self.client.post(self.registration_url, data=invalid_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.registration_url)

        error_message = response.cookies['messages'].value
        # self.assertIn('The two password fields didn’t match.', error_message)
        # # Дополнительные проверки, если необходимо

    def test_same_user_registration(self):
        user1 = self.client.post(self.registration_url, data=self.user_data)
        user2 = self.client.post(self.registration_url, data=self.user_data)
        self.assertEqual(user2.status_code, 302)
        self.assertRedirects(user2, self.registration_url)
        error_message = user2.cookies['messages'].value
        self.assertIn('A user with that username already exists.', error_message)




