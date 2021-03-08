import requests

from django.conf import settings


class RestClient(object):

    PERSON_SLUG_FIELD = 'cpr'
    TAX_YEAR_SLUG_FIELD = 'year'
    INSURANCE_COMPANY_SLUG_FIELD = 'cvr'
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
            headers=self.headers
        )
        return self._handle_response(response)

    def post(self, path, files=None, **data):
        response = requests.post(
            f"{settings.REST_HOST}/rest/{path}/",
            data=data,
            headers=self.headers,
            files=files
        )
        return self._handle_response(response)

    def patch(self, path, **data):
        response = requests.patch(
            f"{settings.REST_HOST}/rest/{path}/",
            data=data,
            headers=self.headers
        )
        return self._handle_response(response)

    def delete(self, path):
        response = requests.delete(
            f"{settings.REST_HOST}/rest/{path}/",
            headers=self.headers,
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
        return self.get('person_tax_year', cpr=cpr)

    def get_policies(self, cpr, year):
        return self.get('policy_tax_year', cpr=cpr, year=year)

    def post_policy(self, id, policy):
        policy_response = self.patch(
            f"policy_tax_year/{id}",
            **{
                k: v for k, v in policy.items()
                if k in [
                    'self_reported_amount', 'preliminary_paid_amount', 'from_pension',
                    'foreign_paid_amount_self_reported',
                    # 'deduction_from_previous_years'
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
