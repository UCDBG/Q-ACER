import numpy as np
import pandas as pd
import re
import os

class statistical_calculation_opt:
    def __init__(self):
        self.column_set = set()

    def _parse_expression(self, expression):
        parts = expression.split('(')
        func_name = parts[0].strip()
        args = parts[1].strip()[:-1]
        args = [arg.strip().replace('"', '') for arg in args.split(',')]
        if len(args) == 1:
            if args[0] in self._known_columns:
                return (func_name, None, args[0])
            else:
                return (func_name, args[0], None)
        elif len(args) == 2:
            return (func_name, args[0], args[1])
        raise ValueError(f"Invalid aggregation expression: {expression}")

    def _compile_condition(self, cond, col_index_map):
        """
        Compile a condition string into a list of (op_func, col_idx, value, logical_op) tuples.
        Done once per unique condition string — result is cached and reused across all clusters.
        """
        cond = cond.replace('"', '')
        conditions = re.split(r'\s+(and|or)\s+', cond)
        operators = {
            '>=': np.greater_equal, '<=': np.less_equal,
            '!=': np.not_equal,     '==': np.equal,
            '>':  np.greater,       '<':  np.less,
        }
        compiled = []
        logical_op = None
        for part in conditions:
            if part.strip() in ('and', 'or'):
                logical_op = part.strip()
                continue
            for op_str, op_func in operators.items():
                if op_str in part:
                    col_name, value = part.split(op_str)
                    compiled.append((op_func, col_index_map[col_name.strip()], float(value.strip()), logical_op))
                    logical_op = None
                    break
        return compiled

    def _apply_compiled_condition(self, numpy_array, compiled_cond):
        """Apply a pre-compiled condition directly to a NumPy array."""
        mask = np.ones(len(numpy_array), dtype=bool)
        for op_func, col_idx, value, logical_op in compiled_cond:
            condition_mask = op_func(numpy_array[:, col_idx], value)
            if logical_op == 'or':
                mask |= condition_mask
            else:
                mask &= condition_mask
        return mask

    def _evaluate_parsed(self, numpy_array, func_name, compiled_cond, col_idx):
        """Evaluate a pre-parsed, pre-compiled aggregation on a NumPy array."""
        if compiled_cond is not None:
            mask = self._apply_compiled_condition(numpy_array, compiled_cond)
            data = numpy_array[mask]
        else:
            data = numpy_array

        if len(data) == 0:
            return 0.0
        if func_name == 'count': return float(len(data))
        if func_name == 'sum':   return float(data[:, col_idx].sum())
        if func_name == 'mean':  return float(data[:, col_idx].mean())
        if func_name == 'min':   return float(data[:, col_idx].min())
        if func_name == 'max':   return float(data[:, col_idx].max())
        raise ValueError(f"Unsupported function: {func_name}")

    def statistical_calculation(self, cluster_tree, df, aggregations, predicates_number,
                                constraint_columns, dataName, dataSize, query_num,
                                leaf_only=False):
        """
        leaf_only=True skips all intermediate/parent nodes, processing only leaf nodes.
        This avoids redundant recomputation over data already covered by child nodes.
        """
        file_name = f"statistical_info_Q{query_num}_{dataName}_{dataSize}.csv"

        # Build column index map once
        col_index_map = {col: idx for idx, col in enumerate(constraint_columns)}
        self._known_columns = set(constraint_columns)

        # Filter to leaf nodes only if requested — eliminates redundant parent computation
        if leaf_only:
            working_tree = [c for c in cluster_tree if not c.get('children')]
        else:
            working_tree = cluster_tree

        # Pre-parse all aggregation expressions once
        parsed_aggregations = []
        for agg_name, agg_expr in aggregations.items():
            func_name, cond, col = self._parse_expression(agg_expr)
            col_idx = col_index_map.get(col) if col else None
            parsed_aggregations.append((agg_name, func_name, cond, col_idx))

        # Pre-compile all unique conditions once — reused across every cluster
        condition_cache = {}
        for _, _, cond, _ in parsed_aggregations:
            if cond and cond not in condition_cache:
                condition_cache[cond] = self._compile_condition(cond, col_index_map)

        # Pre-convert all cluster data to NumPy arrays in one batch
        all_arrays = [np.array(c['Data points'], dtype=np.float64) for c in working_tree]
        all_sliced = [arr[:, predicates_number:] for arr in all_arrays]

        statistical_tree = []
        for clusters, data_points_array, sliced_numpy in zip(working_tree, all_arrays, all_sliced):
            calculation_info = {
                'Predicates points': data_points_array.tolist(),
                'Level':          clusters['Level'],
                'Cluster Id':     clusters['Cluster Id'],
                'Parent level':   clusters['Parent level'],
                'Parent cluster': clusters['Parent cluster'],
                'Data_Min':       np.min(data_points_array, axis=0).tolist(),
                'Data_Max':       np.max(data_points_array, axis=0).tolist(),
                'Count':          len(data_points_array),
            }

            for idx, (agg_name, func_name, cond, col_idx) in enumerate(parsed_aggregations, start=1):
                compiled_cond = condition_cache.get(cond) if cond else None
                result = self._evaluate_parsed(sliced_numpy, func_name, compiled_cond, col_idx)
                calculation_info[f'agg{idx}'] = round(result, 2)

            statistical_tree.append(calculation_info)

        pd.DataFrame(statistical_tree).to_csv(file_name, index=False)
        return statistical_tree

    def points_bounds(self, cluster_points):
        np_data = np.array(cluster_points)
        return {'min': np.min(np_data, axis=0).tolist(), 'max': np.max(np_data, axis=0).tolist()}

    def count(self, num_points):
        return {'count': num_points}



        