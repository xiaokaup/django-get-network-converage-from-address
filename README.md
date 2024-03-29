# django_get_network_converage_from_address

## Commands

```bash
# Creat project
django-admin startproject [projectName]
# Create app
python manage.py startapp [appName]
```

### Packages

```
pip install -r requirements.txt
```

## View

I use a variable `slice_network_coverage_data` to controle amount of data.

## Route

- `http://localhost:8000/network/post/`
- `http://localhost:8000/network/post/async/`

```json
{
  "id1": "CHEZ BREVAL, 29242 Ouessant", // Ok
  "id2": "157 boulevard Mac Donald 75019 Paris" // No operators
}
```

## Goal

input

```json
// This input have not relations with the raw_network_coverage_data.csv
// The waiting time will be long if you use whole raw_network_coverage_data.csv data
// {
//   "id1": "157 boulevard Mac Donald 75019 Paris",
//   "id4": "5 avenue Anatole France 75007 Paris",
//   "id5": "1 Bd de Parc, 77700 Coupvray",
//   "id6": "Place d'Armes, 78000 Versailles",
//   "id7": "17 Rue René Cassin, 51430 Bezannes",
//   "id8": "78 Le Poujol, 30125 L'Estréchure"
// }

// Try to test this input
{
  "id1": "CHEZ BREVAL, 29242 Ouessant", // Ok
  "id2": "157 boulevard Mac Donald 75019 Paris" // No operators
}
```

process:

- Read CSV file, know the coverage measure info of each opeartion for hold places
- Get address, sen to gouv api know the location
- Check every location(lat, lng) if they in coverage 2G, 3G, 4G of every operation (orange, SFR, boygues)

output:

```json
{
  "id1": {
    "orange": { "2G": true, "3G": true, "4G": false },
    "SFR": { "2G": true, "3G": true, "4G": true },
    "bouygues": { "2G": true, "3G": true, "4G": false }
  },
  "id4": {
    "orange": { "2G": true, "3G": true, "4G": false },
    "bouygues": { "2G": true, "3G": false, "4G": false },
    "SFR": { "2G": true, "3G": true, "4G": false }
  }
  // ...
}
```

## Async

```python
import asyncio

async def async_task(number):
    # Simulate an async task
    await asyncio.sleep(1)
    return f"Task {number} completed"

async def main():
    # List of async tasks
    tasks = [async_task(i) for i in range(5)]

    # Run and wait for all tasks to complete (like Promise.all)
    results = await asyncio.gather(*tasks)

    for result in results:
        print(result)

# Run the main function
asyncio.run(main())

```

## Resouce

- [link](https://papernest.notion.site/Backend-developer-technical-test-a6175cee063e438ca0ed229645957e29)
