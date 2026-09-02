# Q-ACER - Efficient Query Repair for Aggregate Constraints

A demonstration for efficient query repair based on aggregate constraints.

## Requirements

- python >= 3.10

## Setup

### Create virtual environement

```sh
just create-venv
```

of use direnv

```sh
direnv allow
```

### install requirements

```sh
pip install -r query-repair-backend/requirements.txt
```

### Build the repair module and install
t
```sh
python -m pip install -e query-repair-module
```

### Install frontend dependencies

```sh
cd query-repair-frontend
npm install
```

## Start system

To run the demo, you have to start the backend and then the frontend. You can use the following [https://github.com/casey/just](just) recipe which also opens the app in your browser.

```sh
just serve
```

or if you prefer the log output to be written to log files:

```sh
just serve-log
```

Alternatively, you can start both manually.

```sh
cd query-repair-backend && fastapi dev
cd query-repair-frontend && npm run dev -- --port 3000
```

## Example scenarios

The demo allows you to specify queries over three example datasets (ACSIncome, Healthcare, TPC-H) by specifying the selection conditions of your query. You then specify an aggregate constraint that is a arithmetic expression over aggregate-filter queries which are evaluated over the result of the query. Intuitively, aggregate constraints are used to specify restrictions that the query result should fulfill. Q-ACER then repairs your query by altering its selection conditions such that the result of the repaired query fulfills the constraint. Aggregate constraints support a wide range of restrictions such as fairness metrics. We provide a few example scenarios to get you inspired.

### Medical Care Program Individual Selection (Healthcare Dataset)

A state Medicaid office is responsible for enrolling
patients into a medical care management program. Due to health-
care equity legislation, the agency must declare a fixed, transparent
set of eligibility criteria upfront. The criteria must balance medical
need, financial vulnerability, and family burden. Only patients satisfying all criteria are pre-qualified for enrollment. 

#### Limiting the amount of heavy smokers

Simultaneously,
the office was advised that no more than 30% of the selected patients
should be heavy smokers (`smoker = 2`) as smoking is considered a
life-style choice that may boost a patients observed medical need. The initial selection of criteria can be expressed as the following SQL query (earning more than 100K, at least 4 complications and at least 3 children:

```sql
SELECT *
FROM Healthcare
WHERE income <= 100
AND complications >= 4
AND num - children >= 3;
```

The requirement that no more than 30% of selected individuals should be heavy smokers can be expressed as the following aggregate constraints: the fraction of heavy smokers (number of selected smokers divided by the total number of selected individuals) should be within `[0.0,0.3]`:

```
agg1 := count(smoker = 2)
agg2 := count()
0.0 <= (agg1/agg2) <= 0.3
```

### ACSIncome dataset

The ACSIncome dataset is data from the American Community Survey (ACS) which records demographic and work-related information about individuals. Consider a scenario where we want to select  successful individuals to receive awards for their success. Individuals are selected based on
 on high working hours (`WKHP`), education (`SCHL`), and class of work (`COW`). We want to ensure that the statistical parity difference between two groups is low (the aggregate constraint), considering the difference between groups `White alone` (`RAC1P = 1`) and `Black or African American alone` (`RAC1P = 2`).

```sql
SELECT * 
FROM acsincome
WHERE WKHP >= 40
      AND SCHL >= 19
      AND COW >= 3;

```

```
agg1 := count(RAC1P == 1 AND PINCP >= 15000)
agg2 := count(RAC1P == 1)
agg3 := count(RAC1P == 2 AND PINCP >= 15000)
agg4 := count(RAC1P == 2)

0.3 <= (agg1/agg2) - (agg3/agg4) <= 0.5
```

