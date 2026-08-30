# Branching in KD fails when no attribute to branch on

```python
predicates = [
        {"field": "income", "op": ">", "value": 100},
        # {"field": "num-children", "op": ">=", "value": 2},
        # {"field": "complications", "op": ">", "value": 3},
    ]
    constraints = {
        "columns": [], # [ "smoker", "" ]
        "aggregations": {
            # "agg1": 'count("smoker == 2")',
            "agg1": 'count()'
        },
        "expression": '1.0 <= (agg1) <= 1000.0',
        "const_num": 0
    }    
```

```
Constraint Columns: []
Existing KD-tree not found. Generating new tree...
Traceback (most recent call last):
  File "<frozen runpy>", line 198, in _run_module_as_main
  File "<frozen runpy>", line 88, in _run_code
  File "/Users/lord_pretzel/Documents/workspace/Q-ACER/query-repair-module/query_repair_module/pp/main.py", line 810, in <module>
    main(
  File "/Users/lord_pretzel/Documents/workspace/Q-ACER/query-repair-module/query_repair_module/pp/main.py", line 718, in main
    cluster_tree = get_clusters(df_merged.values.tolist(), bucket, branch, dataName, const_num, constraint_columns, caching)
                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/lord_pretzel/Documents/workspace/Q-ACER/query-repair-module/query_repair_module/pp/main.py", line 51, in get_clusters
    KD_tree = kd_tree1(df_merged, 3, buckestSize, branchNum)
              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/lord_pretzel/Documents/workspace/Q-ACER/query-repair-module/query_repair_module/pp/kd_tree1.py", line 12, in __init__
    self._root = self._make(points, 0, 0, None)
                 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/lord_pretzel/Documents/workspace/Q-ACER/query-repair-module/query_repair_module/pp/kd_tree1.py", line 61, in _make
    child = self._make(chunk_points, i + 1, level + 1, current_id)
            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/lord_pretzel/Documents/workspace/Q-ACER/query-repair-module/query_repair_module/pp/kd_tree1.py", line 52, in _make
    points.sort(key=lambda x: x[i % self._dim])
  File "/Users/lord_pretzel/Documents/workspace/Q-ACER/query-repair-module/query_repair_module/pp/kd_tree1.py", line 52, in <lambda>
    points.sort(key=lambda x: x[i % self._dim])
                              ~^^^^^^^^^^^^^^^
IndexError: list index out of range
```
