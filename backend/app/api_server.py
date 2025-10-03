"""
新版Web API服务器 - 支持交易记录CRUD操作和Excel导入
"""
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import logging
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
from werkzeug.exceptions import RequestEntityTooLarge
from app.config import Config
from app.database import TradeRecord, SQLiteAdapter
from app.parser import ExcelParser

logger = logging.getLogger(__name__)

def create_app():
    """创建Flask应用"""
    app = Flask(__name__)
    CORS(app)  # 允许跨域请求

    # 配置
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
    app.config['UPLOAD_FOLDER'] = Config.WATCH_FOLDER

    # 初始化数据库 - 强制使用SQLite用于Web API
    storage = SQLiteAdapter(Config.SQLITE_DB_PATH)

    # 确保上传目录存在
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    def allowed_file(filename):
        """检查文件扩展名是否合法"""
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in Config.SUPPORTED_EXTENSIONS

    @app.route('/api/trades', methods=['GET'])
    def get_trades():
        """获取交易记录列表"""
        try:
            # 获取查询参数
            limit = request.args.get('limit', type=int)
            filters = {}

            if request.args.get('symbol'):
                filters['symbol'] = request.args.get('symbol')
            if request.args.get('security_type'):
                filters['security_type'] = request.args.get('security_type')
            if request.args.get('start_date'):
                filters['start_date'] = request.args.get('start_date')
            if request.args.get('end_date'):
                filters['end_date'] = request.args.get('end_date')

            trades = storage.get_trades(limit=limit, filters=filters)

            # 转换为字典格式
            trades_data = [trade.to_dict() for trade in trades]

            return jsonify({
                'trades': trades_data,
                'total': len(trades_data)
            })

        except Exception as e:
            logger.error(f"获取交易记录失败: {str(e)}")
            return jsonify({'error': str(e)}), 500

    @app.route('/api/trades/<int:trade_id>', methods=['GET'])
    def get_trade(trade_id):
        """获取单个交易记录"""
        try:
            trades = storage.get_trades()
            trade = next((t for t in trades if t.id == trade_id), None)

            if not trade:
                return jsonify({'error': '交易记录不存在'}), 404

            return jsonify(trade.to_dict())

        except Exception as e:
            logger.error(f"获取交易记录失败: {str(e)}")
            return jsonify({'error': str(e)}), 500

    @app.route('/api/trades', methods=['POST'])
    def create_trade():
        """创建新交易记录"""
        try:
            data = request.get_json()

            # 创建交易记录对象
            trade = TradeRecord(
                trade_date=data.get('trade_date', ''),
                trade_time=data.get('trade_time', '00:00:00'),
                symbol=data.get('symbol', ''),
                security_name=data.get('security_name', ''),
                security_type=data.get('security_type', 'STOCK'),
                action=data.get('action', ''),
                quantity=data.get('quantity', 0),
                price=data.get('price', 0),
                amount=data.get('amount', 0),
                commission=data.get('commission', 0),
                underlying_symbol=data.get('underlying_symbol', ''),
                strike_price=data.get('strike_price', 0),
                expiration_date=data.get('expiration_date', ''),
                option_type=data.get('option_type', ''),
                source=data.get('source', ''),
                close_date=data.get('close_date', ''),
                close_price=data.get('close_price', 0),
                close_quantity=data.get('close_quantity', 0),
                close_reason=data.get('close_reason', ''),
                trade_rating=data.get('trade_rating', 0),
                trade_type=data.get('trade_type', ''),
                notes=data.get('notes', ''),
                broker=data.get('broker', ''),
                account_id=data.get('account_id', '')
            )

            # 计算净金额
            trade.net_amount = trade.amount + trade.commission

            # 保存到数据库
            success = storage.save_trades([trade])

            if success:
                return jsonify({
                    'trade': trade.to_dict(),
                    'message': '交易记录创建成功'
                }), 201
            else:
                return jsonify({'error': '创建失败'}), 500

        except Exception as e:
            logger.error(f"创建交易记录失败: {str(e)}")
            return jsonify({'error': str(e)}), 500

    @app.route('/api/trades/<int:trade_id>', methods=['PUT'])
    def update_trade(trade_id):
        """更新交易记录"""
        try:
            data = request.get_json()

            # 验证交易记录是否存在
            trades = storage.get_trades()
            existing_trade = next((t for t in trades if t.id == trade_id), None)

            if not existing_trade:
                return jsonify({'error': '交易记录不存在'}), 404

            # 更新字段
            updates = {}
            for key, value in data.items():
                if hasattr(existing_trade, key) and key != 'id':
                    updates[key] = value

            # 如果更新了金额或手续费，重新计算净金额
            if 'amount' in updates or 'commission' in updates:
                updates['net_amount'] = (
                    updates.get('amount', existing_trade.amount) +
                    updates.get('commission', existing_trade.commission)
                )

            # 执行更新
            success = storage.update_trade(trade_id, updates)

            if success:
                # 获取更新后的记录
                updated_trades = storage.get_trades()
                updated_trade = next((t for t in updated_trades if t.id == trade_id), None)

                return jsonify({
                    'trade': updated_trade.to_dict(),
                    'message': '交易记录更新成功'
                })
            else:
                return jsonify({'error': '更新失败'}), 500

        except Exception as e:
            logger.error(f"更新交易记录失败: {str(e)}")
            return jsonify({'error': str(e)}), 500

    @app.route('/api/trades/<int:trade_id>', methods=['DELETE'])
    def delete_trade(trade_id):
        """删除交易记录"""
        try:
            success = storage.delete_trade(trade_id)

            if success:
                return jsonify({'message': '交易记录删除成功'})
            else:
                return jsonify({'error': '删除失败'}), 500

        except Exception as e:
            logger.error(f"删除交易记录失败: {str(e)}")
            return jsonify({'error': str(e)}), 500

    @app.route('/api/statistics', methods=['GET'])
    def get_statistics():
        """获取统计信息"""
        try:
            stats = storage.get_statistics()
            return jsonify(stats)

        except Exception as e:
            logger.error(f"获取统计信息失败: {str(e)}")
            return jsonify({'error': str(e)}), 500

    @app.route('/api/import', methods=['POST'])
    def import_excel():
        """导入Excel文件"""
        try:
            # 检查是否有文件
            if 'file' not in request.files:
                return jsonify({'error': '没有上传文件'}), 400

            file = request.files['file']
            if file.filename == '':
                return jsonify({'error': '没有选择文件'}), 400

            if not allowed_file(file.filename):
                return jsonify({'error': '不支持的文件格式'}), 400

            # 保存上传的文件
            filename = secure_filename(file.filename)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            safe_filename = f"{timestamp}_{filename}"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], safe_filename)
            file.save(filepath)

            logger.info(f"文件上传成功: {filepath}")

            # 解析Excel文件
            parser = ExcelParser()
            trades_data = parser.parse_file(filepath)

            if not trades_data:
                return jsonify({'error': '文件中没有找到有效的交易记录'}), 400

            # 转换为TradeRecord对象
            trades = []
            for trade_data in trades_data:
                trade = TradeRecord.from_dict(trade_data)
                trades.append(trade)

            # 保存到数据库
            success = storage.save_trades(trades)

            if success:
                # 删除临时文件
                try:
                    os.remove(filepath)
                except:
                    pass

                return jsonify({
                    'message': f'成功导入 {len(trades)} 条交易记录',
                    'trades_count': len(trades),
                    'trades': [trade.to_dict() for trade in trades[:10]]  # 返回前10条作为示例
                })
            else:
                return jsonify({'error': '保存数据失败'}), 500

        except RequestEntityTooLarge:
            return jsonify({'error': '文件太大，最大支持16MB'}), 413
        except Exception as e:
            logger.error(f"导入Excel文件失败: {str(e)}")
            return jsonify({'error': f'导入失败: {str(e)}'}), 500

    @app.route('/api/health', methods=['GET'])
    def health_check():
        """健康检查"""
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'storage_type': Config.STORAGE_TYPE
        })

    @app.errorhandler(413)
    def too_large(e):
        """文件过大错误处理"""
        return jsonify({'error': '文件太大，最大支持16MB'}), 413

    @app.errorhandler(404)
    def not_found(e):
        """404错误处理"""
        return jsonify({'error': '接口不存在'}), 404

    @app.errorhandler(500)
    def internal_error(e):
        """500错误处理"""
        logger.error(f"内部服务器错误: {str(e)}")
        return jsonify({'error': '内部服务器错误'}), 500

    return app

def main():
    """启动Web API服务器"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    app = create_app()
    port = int(os.getenv('API_PORT', 5000))
    host = os.getenv('API_HOST', '0.0.0.0')

    logger.info(f"启动Web API服务器: http://{host}:{port}")
    app.run(host=host, port=port, debug=False)

if __name__ == '__main__':
    main()