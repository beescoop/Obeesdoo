Add a 'beneficiary' field on shifts. The beneficiary is the partner (company or individual) for which the shift is done.

- The beneficiary field can be defined on the shift template and on the shift. Beneficiaries can be chosen among the partner that has the field "is_beneficiary" set to True.
- Beneficiaries are displayed on the kanban views in the backend, and the several portal views in the frontend.
- A filter on the beneficiary can be applyed on the irregular shift view in the portal. The filter is based on the beneficiary of the template, not the beneficiary of the shifts.
