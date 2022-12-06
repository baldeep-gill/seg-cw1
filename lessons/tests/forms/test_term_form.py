
from django import forms
from django.test import TestCase
from lessons.forms import TermForm
from lessons.models import Term
from django.utils import timezone
import datetime

class TermFormTestCase(TestCase):
    """Unit tests of the Term form."""

    def setUp(self):
        super(TestCase, self).setUp()

        # We will create a term date that starts 3 months from now and ends 6 months from now
        # This is so the tests never fail due to becoming outdated
        tdelta = datetime.timedelta(weeks=12)
        self.start_term_date = timezone.now() + tdelta
        self.end_term_date = self.start_term_date + tdelta

        self.term_name = 'Autumn Term'
        self.form_input = {
            'name':self.term_name,
            'start_date':f'{self.start_term_date}',
            'end_date':f'{self.end_term_date}',
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
        self.assertEqual(term.start_date, self.start_term_date)
        self.assertEqual(term.end_date, self.end_term_date)

    def test_end_date_cant_be_before_start_date(self):
        self.form_input['end_date'] = '2010-10-10'
        form = TermForm(data=self.form_input)
        self.assertFalse(form.is_valid())

    def test_start_date_cant_overlap_with_other_terms(self):
        tdelta = datetime.timedelta(weeks=12)
        new_term_end_date = self.end_term_date + tdelta

        Term.objects.create(
            name="Winter Term",
            start_date=self.start_term_date,
            end_date=new_term_end_date,
        )
        form = TermForm(data=self.form_input)
        self.assertFalse(form.is_valid())


    def test_end_date_cant_overlap_with_other_terms(self):
        tdelta = datetime.timedelta(weeks=12)
        new_term_start_date = self.start_term_date - tdelta

        Term.objects.create(
            name="Winter Term",
            start_date=new_term_start_date,
            end_date=self.end_term_date,
        )
        form = TermForm(data=self.form_input)
        self.assertFalse(form.is_valid())





