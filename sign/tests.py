from django.test import TestCase
from sign.models import Guest, Event
from django.contrib.auth.models import User


# Create your tests here.
class ModelTest(TestCase):
    def setUp(self):
        Event.objects.create(id=1, name='oneplus 3 event', status=True, limit=2000, address='beijing',
                             start_time='2016-08-31 02:18:22')
        Guest.objects.create(id=1, event_id=1, realname='alen', phone='1377945121', email='alen@mail.com', sign=False)

    def test_event_models(self):
        result = Event.objects.get(name='oneplus 3 event')
        self.assertEqual(result.address, 'beijing')
        self.assertTrue(result.status)

    def test_guest_models(self):
        result = Guest.objects.get(phone='1377945121')
        self.assertEqual(result.realname, 'alen')
        self.assertFalse(result.sign)


class IndexPageTest(TestCase):
    def test_index_page_renders_index_template(self):
        response = self.client.get('/index/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'index.html')


class LoginActionTest(TestCase):
    def setUp(self):
        User.objects.create_user('admintest', 'admintest@mail.com', 'admintest123')

    def test_add_admin(self):
        user = User.objects.get(username='admintest')
        self.assertEqual(user.username, 'admintest')
        self.assertEqual(user.email, 'admintest@mail.com')

    def test_login_action_username_password_null(self):
        test_data = {'username': '', 'password': ''}
        response = self.client.post('/login_action/', data=test_data)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'username or password error!', response.content)

    def test_login_action_username_password_error(self):
        test_data = {'username': 'abc', 'password': '123'}
        response = self.client.post('/login_action/', data=test_data)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'username or password error!', response.content)

    def test_login_action_success(self):
        test_data = {'username': 'admintest', 'password': 'admintest123'}
        response = self.client.post('/login_action/', data=test_data)
        self.assertEqual(response.status_code, 302)


class EventManageTest(TestCase):
    def setUp(self):
        User.objects.create_user('admintest', 'admintest@mail.com', 'admintest123')
        Event.objects.create(id=1, name='oneplus 3 event', status=True, limit=2000, address='beijing',
                             start_time='2016-08-31 02:18:22')
        self.login_user = {'username': 'admintest', 'password': 'admintest123'}

    def test_event_manage_success(self):
        response = self.client.post('/login_action/', data=self.login_user)
        response = self.client.post('/event_manage/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'oneplus 3 event', response.content)
        self.assertIn(b'beijing', response.content)

    def test_event_manage_search_success(self):
        response = self.client.post('/login_action/', data=self.login_user)
        response = self.client.get('/search_name/', {'name': 'oneplus 3 event'})
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'oneplus 3 event', response.content)
        self.assertIn(b'beijing', response.content)


class GuestManageTest(TestCase):
    def setUp(self):
        User.objects.create_user('admintest', 'admintest@mail.com', 'admintest123')
        Event.objects.create(id=1, name='oneplus 3 event', status=True, limit=2000, address='beijing',
                             start_time='2016-08-31 02:18:22')
        self.login_user = {'username': 'admintest', 'password': 'admintest123'}
        Guest.objects.create(realname='alen', phone=18612314456, email='alen@mail.com', sign=0, event_id=1)

    def test_event_manage_success(self):
        response = self.client.post('/login_action/', data=self.login_user)
        response = self.client.get('/guest_manage/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'alen', response.content)
        self.assertIn(b'18612314456', response.content)

    def test_guest_manage_search_success(self):
        response = self.client.post('/login_action/', data=self.login_user)
        response = self.client.get('/search_guest_text/', {'search_text': '18612314456'})
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'alen', response.content)
        self.assertIn(b'18612314456', response.content)


class SignIndexActionTest(TestCase):
    def setUp(self):
        User.objects.create_user('admintest', 'admintest@mail.com', 'admintest123')
        Event.objects.create(id=1, name='apple event', status=True, limit=2000, address='beijing',
                             start_time='2016-08-31 02:18:22')
        Event.objects.create(id=2, name='google event', status=True, limit=1000, address='shanghai',
                             start_time='2016-08-31 05:18:22')
        Guest.objects.create(realname='david', phone=18612314456, email='david@mail.com', sign=0, event_id=1)
        Guest.objects.create(realname='jack', phone=1322432421, email='jack@mail.com', sign=1, event_id=2)
        self.login_user = {'username': 'admintest', 'password': 'admintest123'}

    def test_sign_index_action_phone_null(self):
        response = self.client.post('/login_action/', data=self.login_user)
        response = self.client.post('/sign_index_action/1/', {'phone': ''})
        self.assertEqual(response.status_code, 200)
        self.assertIn(bytes('该手机号用户不存在。', 'utf-8'), response.content)

    def test_sign_index_action_phone_or_event_id_error(self):
        response = self.client.post('/login_action/', data=self.login_user)
        response = self.client.post('/sign_index_action/2/', {'phone': '18612314456'})
        self.assertEqual(response.status_code, 200)
        self.assertIn(bytes('手机号和发布会不匹配。', 'utf-8'), response.content)

    def test_sign_index_action_user_sign_has(self):
        response = self.client.post('/login_action/', data=self.login_user)
        response = self.client.post('/sign_index_action/2/', {'phone': '1322432421'})
        self.assertEqual(response.status_code, 200)
        self.assertIn(bytes('用户已经签到。', 'utf-8'), response.content)

    def test_sign_index_action_sign_success(self):
        response = self.client.post('/login_action/', data=self.login_user)
        response = self.client.post('/sign_index_action/1/', {'phone': '18612314456'})
        self.assertEqual(response.status_code, 200)
        self.assertIn(bytes('成功签到！', 'utf-8'), response.content)
