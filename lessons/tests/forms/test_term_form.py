
from django import forms
from django.test import TestCase
from lessons.forms import TermForm
from lessons.models import Term
import pytz
import datetime

class TermFormTestCase(TestCase):
    """Unit tests of the Term form."""

    # fixtures = [
    #     'lessons/tests/fixtures/default_term.json',
    #     'lessons/tests/fixtures/other_terms.json',
    # ]

    def setUp(self):
        super(TestCase, self).setUp()
        self.term_name = 'Autumn Term'
        self.form_input = {
            'name':self.term_name,
            'start_date':'2024-10-10',
            'end_date':'2025-10-10',
        }

    def test_form_has_necessary_fields(self):
        form = TermForm()
        self.assertIn('name', form.fields)
        self.assertIn('start_date', form.fields)
        self.assertIn('end_date', form.fields)
        start_date_field = form.fields['start_date']
        self.assertTrue(isinstance(start_date_field, forms.DateTimeField))
        end_date_field = form.fields['end_date']
        self.assertTrue(isinstance(end_date_field, forms.DateTimeField))

    def test_valid_term_form(self):
        form = TermForm(data=self.form_input)
        self.assertTrue(form.is_valid())

    def test_form_uses_model_validation(self):
        self.form_input['name'] = ''
        form = TermForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_form_must_save_correctly(self):
        form = TermForm(data=self.form_input)
        before_count = Term.objects.count()
        form.save()
        after_count = Term.objects.count()
        self.assertEqual(after_count, before_count + 1)

        term = Term.objects.get(name=self.term_name)
        self.assertEqual(term.name, self.term_name)
        self.assertEqual(term.start_date, datetime.datetime(year=2024,day=10,month=10,tzinfo=pytz.UTC))
        self.assertEqual(term.end_date, datetime.datetime(year=2025,day=10,month=10,tzinfo=pytz.UTC))

    def test_end_date_cant_be_before_start_date(self):
        self.form_input['end_date'] = '2010-10-10'
        form = TermForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_start_date_cant_overlap_with_other_terms(self):
        start_date = datetime.datetime(year=2024,month=10,day=10,tzinfo=pytz.UTC)
        end_date = datetime.datetime(year=2025,month=10,day=10,tzinfo=pytz.UTC)
        Term.objects.create(
            name="Winter Term",
            start_date=start_date,
            end_date=end_date,
        )
        self.form_input['start_date'] = '2024-10-15'
        self.form_input['end_date'] = '2028-10-15'
        form = TermForm(data=self.form_input)
        self.assertFalse(form.is_valid())


    def test_end_date_cant_overlap_with_other_terms(self):
        start_date = datetime.datetime(year=2024,month=10,day=10,tzinfo=pytz.UTC)
        end_date = datetime.datetime(year=2025,month=10,day=10,tzinfo=pytz.UTC)
        Term.objects.create(
            name="Winter Term",
            start_date=start_date,
            end_date=end_date,
        )
        self.form_input['start_date'] = '2020-10-15'
        self.form_input['end_date'] = '2024-10-15'
        form = TermForm(data=self.form_input)
        self.assertFalse(form.is_valid())





