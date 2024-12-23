Worker status management.


* add "irregular penalty" config in shift settings
* compute next countdown date and future alert date for irregular
  workers, taking into account holidays and exemption status
* compute the future alert date for irregular workers, taking into
  account holidays and exemption status
* compute regular and irregular statuses according to alert start day,
  alert delay, grace delay and time extensions, taking into account
  holidays and exemption status
* recompute status and counters when a shift undergoes a state change
* postpone alert start time based on holidays and extension status
* handle is_regular and is_compensation consistency on shifts, on worker
  change and by raising a validation error if the fields are not
  properly set
