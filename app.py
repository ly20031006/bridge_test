# *_* coding : UTF-8 *_*
# 开发团队  ：  LiYan
# 开发人员  ：  LiYan
# 开发时间  ：  2024/12/14  20:22
# 文件名称  :  app.PY
# 开发工具  :  PyCharm
from flask import Flask, request, jsonify
import os
import subprocess

app = Flask(__name__)


@app.route('/set_parameters', methods=['POST'])
def set_parameters():
    data = request.json
    stock_code = data.get('stock_code')
    start_date = data.get('start_date')
    end_date = data.get('end_date')

    if not all([stock_code, start_date, end_date]):
        return jsonify({'error': '缺少参数'}), 400

    with open('parameters.txt', 'w') as f:
        f.write(f'{stock_code}\n{start_date}\n{end_date}')

    return jsonify({'message': '参数设置成功'}), 200


@app.route('/get_results', methods=['GET'])
def get_results():
    if not os.path.exists('results.txt'):
        return jsonify({'error': '没有找到结果'}), 404

    with open('results.txt', 'r') as f:
        lines = f.readlines()
        total_return = float(lines[0].strip())
        final_value = float(lines[1].strip())

    return jsonify({
        'total_return': total_return,
        'final_value': final_value
    }), 200


def run_backtest():
    if not os.path.exists('parameters.txt'):
        raise Exception("参数文件未找到")

    with open('parameters.txt', 'r') as f:
        lines = f.readlines()
        stock_code = lines[0].strip()
        start_date = lines[1].strip()
        end_date = lines[2].strip()

    result = subprocess.run(['python', 'backtest/ma_strategy.py', stock_code, start_date, end_date],
                            capture_output=True, text=True)

    if result.returncode != 0:
        raise Exception(result.stderr)

    output_lines = result.stdout.split('\n')
    total_return_line = next(line for line in output_lines if 'Total Return:' in line)
    final_value_line = next(line for line in output_lines if 'Final Value:' in line)

    total_return_str = total_return_line.split(': ')[1].replace('%', '')
    total_return = float(total_return_str) / 100
    final_value = float(final_value_line.split(': ')[1])

    with open('results.txt', 'w') as f:
        f.write(f'{total_return}\n{final_value}')

    return total_return, final_value


if __name__ == '__main__':
    app.run(debug=True)






