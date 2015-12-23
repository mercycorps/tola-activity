from django.forms import ModelForm
from indicators.models import Indicator, CollectedData, Objective, StrategicObjective
from activitydb.models import Program, SiteProfile, Documentation, ProjectAgreement
from crispy_forms.helper import FormHelper
from crispy_forms.layout import *
from crispy_forms.bootstrap import *
from crispy_forms.layout import Layout, Submit, Reset, Field
from functools import partial
import floppyforms.__future__ as forms
from tola.util import getCountry


class DatePicker(forms.DateInput):
    """
    Use in form to create a Jquery datepicker element
    """
    template_name = 'datepicker.html'

    DateInput = partial(forms.DateInput, {'class': 'datepicker'})


class IndicatorForm(forms.ModelForm):

    class Meta:
        model = Indicator
        exclude = ['create_date','edit_date']

    def __init__(self, *args, **kwargs):
        #get the user object to check permissions with
        self.request = kwargs.pop('request')
        self.program = kwargs.pop('program')
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-sm-2'
        self.helper.field_class = 'col-sm-6'
        self.helper.form_error_title = 'Form Errors'
        self.helper.error_text_inline = True
        self.helper.help_text_inline = True
        self.helper.html5_required = True
        self.helper.layout = Layout(

            HTML("""<br/>"""),
            TabHolder(
                Tab('Summary',
                     Fieldset('',
                        'program','sector','objectives','strategic_objectives'
                        ),
                ),
                Tab('Performance',
                     Fieldset('Performance',
                        'name', 'type', 'level', 'number', 'source', 'definition', 'disaggregation','owner', 'country','indicator_type',PrependedText('key_performance_indicator','')
                        ),
                ),
                Tab('Targets',
                    Fieldset('Targets',
                             'baseline','lop_target',
                             ),
                ),
                Tab('Data Acquisition',
                    Fieldset('Data Acquisition',
                        'means_of_verification','data_collection_method','responsible_person',
                        ),
                ),
                Tab('Analysis and Reporting',
                    Fieldset('Analysis and Reporting',
                        'method_of_analysis','information_use', 'reporting_frequency','comments'
                    ),
                ),
                Tab('Approval',
                    Fieldset('Approval',
                        'approval', 'filled_by', 'approved_by',
                    ),
                ),
            ),
            HTML("""
                  {% if getExternalServiceRecord %}
                      <br/>
                      <div class='panel panel-default'>
                      <!-- Default panel contents -->
                      <div class='panel-heading'>External Indicator Service</div>
                          <!-- Table -->
                          <table class="table">
                           <tr>
                             <th>Service Name</th>
                             <th>View Guidance</th>
                           </tr>
                        {% for item in getExternalServiceRecord %}
                           <tr>
                            <td>{{ item.external_service.name }}</td>
                            <td><a target="_new" href='{{ item.full_url }}'>View</a>
                           </tr>
                        {% endfor %}
                         </table>
                      </div>
                  {% endif %}
             """),

            HTML("""<br/>"""),
            FormActions(
                Submit('submit', 'Save', css_class='btn-default'),
                Reset('reset', 'Reset', css_class='btn-warning')
            )
        )

        super(IndicatorForm, self).__init__(*args, **kwargs)
        
        #override the program queryset to use request.user for country
        countries = getCountry(self.request.user)
        self.fields['program'].queryset = Program.objects.filter(funding_status="Funded", country__in=countries)
        self.fields['objectives'].queryset = Objective.objects.all().filter(program__id=self.program)
        self.fields['strategic_objectives'].queryset = StrategicObjective.objects.filter(country__in=countries)


class CollectedDataForm(forms.ModelForm):

    class Meta:
        model = CollectedData
        exclude = ['create_date', 'edit_date']

    date_collected = forms.DateField(widget=DatePicker.DateInput(), required=True)

    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.request = kwargs.pop('request')
        self.program = kwargs.pop('program')
        self.helper.form_method = 'post'
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-sm-2'
        self.helper.field_class = 'col-sm-6'
        self.helper.form_error_title = 'Form Errors'
        self.helper.error_text_inline = True
        self.helper.help_text_inline = True
        self.helper.html5_required = True
        self.helper.form_tag = True
        self.helper.layout = Layout(

            HTML("""<br/>"""),

            Fieldset('Collected Data',
                'targeted', 'achieved', 'date_collected','indicator', 'program','description',

            ),

            HTML("""<br/>"""),

            Fieldset('Evidence',
                'agreement','method','evidence','tola_table',
                HTML("""<a class="output" data-toggle="modal" data-target="#myModal" href="/indicators/collecteddata_import/{{ program_id }}/{{ indicator_id }}/">Import Evidence From Tola Tables</a>"""),

            ),



                MultiField(
                        "",
                        HTML("""<br/>
                                {% if getDisaggregationLabel and not getDisaggregationValue%}
                                    <div class='panel panel-default'>
                                        <!-- Default panel contents -->
                                        <div class='panel-heading'>New Disaggregations</div>
                                          <!-- Table -->
                                          <table class="table">
                                            <tr>
                                            <th>Disaggregation Level</th>
                                            <th>Actuals</th>
                                            </tr>
                                            {% for item in getDisaggregationLabel %}
                                            <tr>
                                                <td>{{ item.label }}</td>
                                                <td><input type="text" name="{{ item.id }}" value=""></td>
                                            </tr>
                                            {% endfor %}
                                          </table>
                                    </div>
                                {% else %}
                                    <h4>Disaggregation Levels Not Entered For This Indicator</h4>
                                    <a href="/indicators/indicator_update/{{ indicator_id }}">Add a Disaggregation</a>
                                {% endif %}

                                {% if getDisaggregationValue %}
                                    <div class='panel panel-default'>
                                        <!-- Default panel contents -->
                                        <div class='panel-heading'>Existing Disaggregations</div>

                                          <!-- Table -->
                                          <table class="table">
                                            <tr>
                                            <th>Disaggregation Level</th>
                                            <th>Actuals</th>
                                            </tr>
                                            {% for item in getDisaggregationValue %}
                                            <tr>
                                                <td>{{ item.disaggregation_label.label }}</td>
                                                <td><input type="text" name="{{ item.disaggregation_label.id }}" value="{{ item.value }}"></td>
                                            </tr>
                                            {% endfor %}
                                          </table>

                                    </div>
                                {% endif %}
                             """),
                ),

            HTML("""<br/>"""),
            FormActions(
                Submit('submit', 'Save', css_class='btn-default'),
                Reset('reset', 'Reset', css_class='btn-warning')
            )
        )

        super(CollectedDataForm, self).__init__(*args, **kwargs)

        #override the program queryset to use request.user for country
        self.fields['evidence'].queryset = Documentation.objects.filter(program=self.program)

        #override the program queryset to use request.user for country
        self.fields['agreement'].queryset = ProjectAgreement.objects.filter(program=self.program)

        self.fields['indicator'].queryset = Indicator.objects.filter(name__isnull=False)


