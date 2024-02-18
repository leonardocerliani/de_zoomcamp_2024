## Analytics engineering basics

### Data roles
- **Data Engineer** : prepares and maintain the infrastructure the data team needs
- **Analytics Engineer** : Introduces the good sw engineering practices to the efforts of data anaysts and data scientists
- **Data Analyst** : Use the data to answer questions and solve problems

### Data Lifecycle
1. Loading
2. Storing : cloud data warehouses like snowflake, bigquery, redshift
3. Data modelling : with tools like dbt or Dataform
4. Data presentation : BI tools like google data studio, looker, more or tableau

NB: note that the analytics parts has totally disappeared ;)  

### ETL vs ELT
In the end, ELT this simply means that both transformation and analytics/reporting are done in the data warehouse

- ETL
  - slightly more stable and compliant data analysis
  - higher storage and compute costs
- ELT
  - faster and more flexible data analysis
  - lower cost and lower maintainance

### Kimball's dimensional modeling
tidy data

### Elements of dimensional modeling

- Fact tables
  - measurements, metrics or facts
  - represents business _processes_
  - "verbs"
- Dimnesions tables
  - business _entities_
  - provide context to a business
  - "nouns"

### Architecture of dimensional modeling

Great analogy with a restaurant:

- Stage area : suppliers (of ingredients, cutleries, machines)
  - contains the raw data
  - not meant to be exposes to everyone  
- Processing area : the kitchen
  - from raw data to data models
  - focuses on efficiency
  - ensuring standards
- Presentation area : the restaurant zaal
  - final presentation of the data
  - exposure to business stakeholders

## What is DBT
A tool that allows us to write code to transform raw data using sw engineering practices (e.g. version control)
