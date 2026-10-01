# MiniEDC Data Validation Specification

Rule catalogue: **50 edit checks** across DM, VS, AE, and CM.

| Check ID | Form | Field | Rule | Severity | Query Text |
| --- | --- | --- | --- | --- | --- |
| DM001 | DM | subject_id | Subject ID is required. | Critical | Please confirm the missing subject identifier. |
| DM002 | DM | subject_id | Subject ID must be unique in the Demographics form. | Major | Please resolve the duplicate Demographics record for this subject. |
| DM003 | DM | site_id | Site is required and must be one of S01, S02, S03, S04, S05, S06. | Major | Please confirm the subject's assigned site. |
| DM004 | DM | consent_date | Informed consent date is required. | Critical | Please enter the date informed consent was obtained. |
| DM005 | DM | birth_date | Date of birth is required. | Major | Please enter the subject's date of birth. |
| DM006 | DM | consent_date | Consent date must be later than the date of birth. | Critical | Please verify the consent date and date of birth. |
| DM007 | DM | birth_date | Age at consent must be between 18 and 85 years. | Major | Please verify the subject's date of birth and eligibility age. |
| DM008 | DM | initials | Subject initials are required. | Minor | Please enter the subject's initials per the CRF guidelines. |
| DM009 | DM | sex | Sex must be Female, Male, Other, or Unknown. | Minor | Please select a permitted sex value or correct the entry. |
| VS001 | VS | subject_id | Subject ID is required. | Critical | Please confirm the subject identifier for this vital-sign record. |
| VS002 | VS | site_id | Site is required. | Major | Please enter the site that collected these vital signs. |
| VS003 | VS | visit_date | Visit date is required and must be a valid date. | Major | Please enter a valid date for this visit. |
| VS004 | VS | visit_date | Visit date must be on or after informed consent. | Critical | Please verify that this visit occurred after informed consent. |
| VS005 | VS | systolic_bp | Systolic blood pressure is required. | Major | Please enter the systolic blood pressure or document why it is missing. |
| VS006 | VS | systolic_bp | Systolic blood pressure must be between 70 and 250 mmHg. | Major | Please verify the systolic blood pressure and confirm the value in mmHg. |
| VS007 | VS | diastolic_bp | Diastolic blood pressure is required. | Major | Please enter the diastolic blood pressure or document why it is missing. |
| VS008 | VS | diastolic_bp | Diastolic blood pressure must be between 40 and 150 mmHg. | Major | Please verify the diastolic blood pressure and confirm the value in mmHg. |
| VS009 | VS | systolic_bp | Systolic blood pressure must be greater than diastolic blood pressure. | Major | Please verify the systolic and diastolic blood pressure values. |
| VS010 | VS | pulse | Pulse must be between 30 and 220 beats per minute. | Major | Please verify the pulse value and confirm the unit is beats per minute. |
| VS011 | VS | weight | Weight must be between 30 and 250 kilograms. | Major | Please verify the weight value and source unit. |
| VS012 | VS | weight_unit | Weight must be recorded in kilograms (kg). | Minor | Please convert the source weight to kilograms and update the recorded unit. |
| VS013 | VS | visit | Visit must be one of: Screening, Baseline, Week 2, Week 4, Week 8. | Major | Please select a scheduled visit from the permitted visit list. |
| VS014 | VS | visit | A subject may have only one record per scheduled visit. | Major | Please resolve the duplicate subject and visit record. |
| VS015 | VS | visit_date | Scheduled visit dates must not move backward in visit order. | Major | Please verify the visit date sequence for this subject. |
| VS016 | VS | site_id | Vital-sign site must match the subject's Demographics site. | Major | Please confirm the site against the subject's Demographics record. |
| VS017 | VS | subject_id | Subject must exist in the Demographics form. | Critical | Please confirm the subject identifier or add the Demographics record first. |
| AE001 | AE | ae_term | Adverse event term is required. | Major | Please enter the adverse event term using the study coding convention. |
| AE002 | AE | start_date | Adverse event start date is required and must be valid. | Major | Please enter a valid adverse event start date. |
| AE003 | AE | end_date | Adverse event end date must not precede its start date. | Major | Please verify the adverse event start and end dates. |
| AE004 | AE | severity | Severity must be Mild, Moderate, or Severe. | Major | Please select a permitted adverse event severity. |
| AE005 | AE | serious | Seriousness must be Yes or No. | Major | Please assess and record whether the event meets seriousness criteria. |
| AE006 | AE | relationship | Relationship must be Unrelated, Unlikely, Possible, Probable, or Related. | Major | Please assess and record the event's relationship to study treatment. |
| AE007 | AE | outcome | Outcome must be a permitted study outcome. | Minor | Please select a permitted adverse event outcome. |
| AE008 | AE | ongoing | Ongoing must be Yes or No. | Major | Please indicate whether the adverse event is ongoing. |
| AE009 | AE | end_date | End date is required when the event is not ongoing. | Major | Please enter an end date or update the ongoing status. |
| AE010 | AE | start_date | Adverse event start date must be on or after consent. | Critical | Please verify the event start date against the informed consent date. |
| AE011 | AE | subject_id | Subject must exist in the Demographics form. | Critical | Please confirm the subject identifier or add the Demographics record first. |
| AE012 | AE | site_id | Adverse event site must match the subject's Demographics site. | Major | Please confirm the site against the subject's Demographics record. |
| AE013 | AE | site_id | Site is required. | Major | Please enter the site that reported this adverse event. |
| CM001 | CM | medication | Concomitant medication name is required. | Major | Please enter the medication name or document that no medication was taken. |
| CM002 | CM | start_date | Medication start date is required and must be valid. | Major | Please enter a valid medication start date. |
| CM003 | CM | end_date | Medication end date must not precede its start date. | Major | Please verify the medication start and end dates. |
| CM004 | CM | dose | Dose must be a positive number. | Major | Please verify the medication dose and enter a positive numeric value. |
| CM005 | CM | dose_unit | Dose unit must be mg, mcg, g, mL, or IU. | Major | Please correct the dose unit to a permitted value. |
| CM006 | CM | indication | Medication indication is required. | Minor | Please enter the reason the medication is being taken. |
| CM007 | CM | ongoing | Ongoing must be Yes or No. | Major | Please indicate whether the medication is ongoing. |
| CM008 | CM | end_date | End date is required when medication is not ongoing. | Major | Please enter an end date or update the ongoing status. |
| CM009 | CM | subject_id | Subject must exist in the Demographics form. | Critical | Please confirm the subject identifier or add the Demographics record first. |
| CM010 | CM | site_id | Concomitant medication site must match the subject's Demographics site. | Major | Please confirm the site against the subject's Demographics record. |
| CM011 | CM | site_id | Site is required. | Major | Please enter the site that collected this medication history. |
