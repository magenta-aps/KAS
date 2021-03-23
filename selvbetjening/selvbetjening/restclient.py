import requests

from django.conf import settings


class RestClient(object):

    PERSON_SLUG_FIELD = 'cpr'
    TAX_YEAR_SLUG_FIELD = 'year'
    INSURANCE_COMPANY_SLUG_FIELD = 'res'
    PERSON_TAX_YEAR_SLUG_FIELD = 'id'

    @property
    def headers(self):
        return {'Authorization': f"Token {settings.REST_TOKEN}"}

    def _handle_response(self, response):
        if response.status_code == 204:
            return None
        elif response.ok:
            return response.json()
        else:
            response.raise_for_status()

    def get(self, path, **params):
        response = requests.get(
            f"{settings.REST_HOST}/rest/{path}/",
            params=params,
            headers=self.headers,
            verify=False,  # settings.REST_CA_CERT,
        )
        return self._handle_response(response)

    def post(self, path, files=None, **data):
        response = requests.post(
            f"{settings.REST_HOST}/rest/{path}/",
            data=data,
            headers=self.headers,
            files=files,
            verify=False,  # settings.REST_CA_CERT,
        )
        return self._handle_response(response)

    def patch(self, path, **data):
        response = requests.patch(
            f"{settings.REST_HOST}/rest/{path}/",
            data=data,
            headers=self.headers,
            verify=False,  # settings.REST_CA_CERT,
        )
        return self._handle_response(response)

    def delete(self, path):
        response = requests.delete(
            f"{settings.REST_HOST}/rest/{path}/",
            headers=self.headers,
            verify=False,  # settings.REST_CA_CERT,
        )
        return self._handle_response(response)

    def obtain(self, path, multiple=False, **params):
        items = self.get(path, **params)
        if len(items) == 0:
            items = [self.post(path, **params)]
        if multiple:
            return items
        return items[0]

    def get_person_tax_years(self, cpr):
        person_tax_years = self.get('person_tax_year', cpr=cpr)
        for p in person_tax_years:
            p['tax_year'] = self.get_tax_year(p['tax_year'])

    def get_person_tax_year(self, cpr, year):
        person_tax_years = self.get('person_tax_year', cpr=cpr, year=year)
        if len(person_tax_years) == 1:
            person_tax_year = person_tax_years[0]
            person_tax_year['tax_year'] = self.get_tax_year(person_tax_year['tax_year'])
            return person_tax_year

    def get_tax_year(self, year):
        tax_years = self.get('tax_year', year=year)
        return tax_years[0] if len(tax_years) else None

    def get_person_tax_year_by_id(self, id):
        person_tax_year = self.get(f"person_tax_year/{id}")
        person_tax_year['tax_year'] = self.get_tax_year(person_tax_year['tax_year'])
        return person_tax_year

    def get_policies(self, **params):
        policies = self.get('policy_tax_year', **params)
        for p in policies:
            if type(p['person_tax_year']) == int:
                p['person_tax_year'] = self.get_person_tax_year_by_id(p['person_tax_year'])
            if type(p['pension_company']) == int:
                p['pension_company'] = self.get_pension_company_by_id(p['pension_company'])
        return policies

    def get_pension_companies(self):
        return self.get("pension_company")

    def get_pension_company_by_id(self, id):
        return self.get(f"pension_company/{id}")

    def create_pension_company(self, name):
        return self.post("pension_company", name=name)

    def update_person_tax_year(self, id, person_tax_year):
        person_response = self.patch(
            f"person_tax_year/{id}",
            **{
                k: v for k, v in person_tax_year.items()
                if k in [
                    'foreign_pension_notes', 'general_notes'
                ]
            }
        )
        return person_response

    def update_policy(self, id, policy):
        policy_response = self.patch(
            f"policy_tax_year/{id}",
            **{
                k: v for k, v in policy.items()
                if k in [
                    'self_reported_amount',
                ]
            }
        )
        if 'files' in policy:
            for file in policy['files']:
                (fileobject, description) = file
                self.post(
                    'policy_document',
                    policy_tax_year=id,
                    name=fileobject.name,
                    description=description,
                    files={'file': fileobject}
                )
        if 'existing_files' in policy:
            for id, data in policy['existing_files'].items():
                if data.get('keep') is False:
                    self.delete(
                        f"policy_document/{id}"
                    )
                elif data.get('description') is not None:
                    self.patch(
                        f"policy_document/{id}",
                        description=data.get('description')
                    )
        return policy_response

    def create_policy(self, policy):
        policy_response = self.post(
            "policy_tax_year",
            **{
                k: v for k, v in policy.items()
                if k in [
                    'self_reported_amount', 'preliminary_paid_amount', 'from_pension',
                    'foreign_paid_amount_self_reported', 'pension_company', 'person_tax_year',
                    'policy_number'
                ]
            }
        )
        if 'files' in policy:
            for file in policy['files']:
                (fileobject, description) = file
                self.post(
                    'policy_document',
                    policy_tax_year=policy_response['id'],
                    name=fileobject.name,
                    description=description,
                    files={'file': fileobject}
                )
        return policy_response
