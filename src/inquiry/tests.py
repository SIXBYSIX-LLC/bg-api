from common.tests import TestCase
from catalog.factories import ProductFactory
from inquiry.factories import MessageBaseFactory, MessageFactory
from usr.factories import UserFactory
from . import factories


class InquiryTest(TestCase):
    def test_create_thread_with_message(self):
        user = UserFactory()
        product = ProductFactory(user=user)
        resp = self.user_client.post('/inquiries',
                                     data={'product': product.id, 'text': 'Lorem ism op gism'})
        self.assertEqual(resp.status_code, self.status_code.HTTP_201_CREATED)
        self.assertEqual(resp.data['to_user'], user.id)
        self.assertEqual(resp.data['user'], self.user.id)

    def test_create_thread(self):
        user = UserFactory()
        product = ProductFactory(user=user)
        resp = self.user_client.post('/inquiries', data={'product': product.id})
        self.assertEqual(resp.status_code, self.status_code.HTTP_201_CREATED)
        self.assertEqual(resp.data['to_user'], user.id)
        self.assertEqual(resp.data['user'], self.user.id)

    def test_create_thread_same_product(self):
        product = ProductFactory(user=self.user)
        # To ensure that thread id for same product stays same
        threads = factories.ThreadFactory.create_batch(10, product=product, user=self.user)
        resp = self.user_client.post('/inquiries', data={'product': product.id})
        self.assertEqual(resp.data['thread'], threads[3].id)

    def test_list_threads(self):
        user = UserFactory()
        product = ProductFactory(user=user)
        factories.ThreadFactory.create_batch(10, product=product, user=user)

        factories.ThreadFactory.create(product=product, user=self.user)

        resp = self.user_client.get('/inquiries')
        self.assertEqual(resp.meta['count'], 1)

    def test_create_message_using_thread(self):
        product = ProductFactory(user=UserFactory())
        thread = factories.ThreadFactory.create(product=product, user=self.user)

        resp = self.user_client.post('/inquiries/%s/messages' % thread.id,
                                     data=MessageBaseFactory())
        self.assertEqual(resp.status_code, self.status_code.HTTP_201_CREATED)

    def test_test_thread_unread_count(self):
        user = UserFactory()
        product = ProductFactory(user=user)
        thread = factories.ThreadFactory.create(product=product, user=self.user)

        # Let self.user to write 2 message
        MessageFactory.create_batch(2, user=self.user, thread=thread)
        # Let new user to write 5 message
        MessageFactory.create_batch(5, user=user, thread=thread)

        # Assert 5 unread when self.user opens the thread
        resp = self.user_client.get('/inquiries')
        self.assertEqual(resp.data[0]['unread_count'], 5)

        # Assert 2 unread when user opens the thread
        resp = self.get_client(user).get('/inquiries')
        self.assertEqual(resp.data[0]['unread_count'], 2)

    def test_list_message(self):
        user = UserFactory()
        product = ProductFactory(user=user)
        thread = factories.ThreadFactory.create(product=product, user=self.user)

        # Let self.user to write 2 message
        MessageFactory.create_batch(2, user=self.user, thread=thread)
        # Let new user to write 5 message
        MessageFactory.create_batch(5, user=user, thread=thread)

        # Assert 7 when self.user opens the thread
        resp = self.user_client.get('/inquiries/%s/messages' % thread.id)
        self.assertEqual(resp.meta['count'], 7)
        # Ensure mark as read
        resp = self.user_client.get('/inquiries')
        self.assertEqual(resp.data[0]['unread_count'], 0)

        # Assert 7 when suser opens the thread
        resp = self.get_client(user).get('/inquiries/%s/messages' % thread.id)
        self.assertEqual(resp.meta['count'], 7)
        # Ensure mark as read
        resp = self.get_client(user).get('/inquiries')
        self.assertEqual(resp.data[0]['unread_count'], 0)
