import React, { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, BarChart, Bar, ScatterChart, Scatter } from 'recharts';
import { TrendingUp, TrendingDown, Activity, BarChart3, PieChart, AlertTriangle } from 'lucide-react';

const TechnicalAnalysisApp = () => {
  const [stockData, setStockData] = useState([]);
  const [selectedStock, setSelectedStock] = useState(null);
  const [analysisView, setAnalysisView] = useState('overview');

  useEffect(() => {
    // 模拟读取CSV数据
    const loadData = async () => {
      try {
        const fileContent = await window.fs.readFile('white_wine_stock_analysis_20250701_064525.csv', { encoding: 'utf8' });
        
        // 简单解析CSV（这里用分割方式，实际项目中应该用专业库）
        const lines = fileContent.split('\n');
        const headers = lines[0].split(',');
        const data = lines.slice(1).filter(line => line.trim()).map(line => {
          const values = line.split(',');
          const obj = {};
          headers.forEach((header, index) => {
            const value = values[index]?.replace(/"/g, '');
            if (header === 'current_price' || header === 'rsi' || header === 'pe_ratio' || 
                header === 'pb_ratio' || header === 'roe' || header === 'max_drawdown' ||
                header === 'technical_score' || header === 'fundamental_score' || header === 'total_score') {
              obj[header] = parseFloat(value) || 0;
            } else {
              obj[header] = value;
            }
          });
          return obj;
        });
        
        setStockData(data);
        if (data.length > 0) {
          setSelectedStock(data[0]);
        }
      } catch (error) {
        console.error('数据加载失败:', error);
        // 使用示例数据
        const sampleData = [
          {
            symbol: '600519.SH',
            name: '贵州茅台',
            current_price: 1405.57,
            rsi: 32.68,
            pe_ratio: 19.82,
            pb_ratio: 7.45,
            roe: 0.28,
            max_drawdown: -0.35,
            technical_score: 6.5,
            fundamental_score: 9,
            total_score: 15.5
          }
        ];
        setStockData(sampleData);
        setSelectedStock(sampleData[0]);
      }
    };
    
    loadData();
  }, []);

  // 计算技术指标
  const calculateTechnicalIndicators = (stock) => {
    if (!stock) return {};

    const rsi = stock.rsi || 0;
    const price = stock.current_price || 0;
    const peRatio = stock.pe_ratio || 0;
    const pbRatio = stock.pb_ratio || 0;
    const roe = (stock.roe || 0) * 100;
    const maxDrawdown = (stock.max_drawdown || 0) * 100;

    // RSI 信号判断
    const getRSISignal = (rsi) => {
      if (rsi > 70) return { signal: '超买', color: 'text-red-500', advice: '考虑卖出' };
      if (rsi < 30) return { signal: '超卖', color: 'text-green-500', advice: '考虑买入' };
      return { signal: '中性', color: 'text-gray-500', advice: '观望' };
    };

    // PE估值判断
    const getPESignal = (pe) => {
      if (pe > 25) return { signal: '高估', color: 'text-red-500' };
      if (pe < 15) return { signal: '低估', color: 'text-green-500' };
      return { signal: '合理', color: 'text-blue-500' };
    };

    // PB估值判断
    const getPBSignal = (pb) => {
      if (pb > 3) return { signal: '偏高', color: 'text-red-500' };
      if (pb < 1.5) return { signal: '偏低', color: 'text-green-500' };
      return { signal: '正常', color: 'text-blue-500' };
    };

    return {
      rsi: {
        value: rsi.toFixed(2),
        ...getRSISignal(rsi)
      },
      pe: {
        value: peRatio.toFixed(2),
        ...getPESignal(peRatio)
      },
      pb: {
        value: pbRatio.toFixed(2),
        ...getPBSignal(pbRatio)
      },
      roe: {
        value: roe.toFixed(2) + '%',
        signal: roe > 15 ? '优秀' : roe > 10 ? '良好' : '一般',
        color: roe > 15 ? 'text-green-500' : roe > 10 ? 'text-blue-500' : 'text-gray-500'
      },
      drawdown: {
        value: maxDrawdown.toFixed(2) + '%',
        signal: maxDrawdown < -50 ? '深度回撤' : maxDrawdown < -30 ? '中度回撤' : '轻微回撤',
        color: maxDrawdown < -50 ? 'text-red-500' : maxDrawdown < -30 ? 'text-yellow-500' : 'text-green-500'
      }
    };
  };

  // 生成通达信风格的技术分析报告
  const generateTechnicalReport = (stock) => {
    if (!stock) return '';

    const indicators = calculateTechnicalIndicators(stock);
    const technicalReasons = stock.technical_reasons || '';
    const fundamentalReasons = stock.fundamental_reasons || '';

    return {
      technical: technicalReasons.replace(/\[|\]|'/g, '').split(',').map(s => s.trim()),
      fundamental: fundamentalReasons.replace(/\[|\]|'/g, '').split(',').map(s => s.trim())
    };
  };

  const indicators = selectedStock ? calculateTechnicalIndicators(selectedStock) : {};
  const report = selectedStock ? generateTechnicalReport(selectedStock) : { technical: [], fundamental: [] };

  // 准备图表数据
  const chartData = stockData.map(stock => ({
    name: stock.name.length > 4 ? stock.name.slice(0, 4) : stock.name,
    价格: stock.current_price,
    RSI: stock.rsi,
    PE: stock.pe_ratio,
    技术评分: stock.technical_score,
    基本面评分: stock.fundamental_score,
    综合评分: stock.total_score
  }));

  const rsiData = stockData.map(stock => ({
    name: stock.name.length > 4 ? stock.name.slice(0, 4) : stock.name,
    RSI: stock.rsi,
    超买线: 70,
    超卖线: 30
  }));

  return (
    <div className="min-h-screen bg-gray-900 text-white p-4">
      <div className="max-w-7xl mx-auto">
        {/* 标题栏 */}
        <div className="bg-gray-800 rounded-lg p-4 mb-6 border-l-4 border-blue-500">
          <h1 className="text-2xl font-bold flex items-center gap-2">
            <BarChart3 className="text-blue-400" />
            白酒股票技术指标分析系统
          </h1>
          <p className="text-gray-400 mt-2">类通达信风格技术分析工具</p>
        </div>

        {/* 导航栏 */}
        <div className="flex gap-2 mb-6">
          {['overview', 'technical', 'fundamental', 'charts'].map(view => (
            <button
              key={view}
              onClick={() => setAnalysisView(view)}
              className={`px-4 py-2 rounded transition-colors ${
                analysisView === view 
                  ? 'bg-blue-600 text-white' 
                  : 'bg-gray-700 hover:bg-gray-600'
              }`}
            >
              {view === 'overview' ? '总览' : 
               view === 'technical' ? '技术面' :
               view === 'fundamental' ? '基本面' : '图表'}
            </button>
          ))}
        </div>

        {/* 股票选择器 */}
        <div className="bg-gray-800 rounded-lg p-4 mb-6">
          <label className="block text-sm font-medium mb-2">选择股票:</label>
          <select
            value={selectedStock?.symbol || ''}
            onChange={(e) => {
              const stock = stockData.find(s => s.symbol === e.target.value);
              setSelectedStock(stock);
            }}
            className="bg-gray-700 border border-gray-600 rounded px-3 py-2 w-full max-w-md"
          >
            {stockData.map(stock => (
              <option key={stock.symbol} value={stock.symbol}>
                {stock.symbol} - {stock.name}
              </option>
            ))}
          </select>
        </div>

        {/* 主要内容区域 */}
        {analysisView === 'overview' && selectedStock && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* 基本信息卡片 */}
            <div className="bg-gray-800 rounded-lg p-6">
              <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
                <Activity className="text-green-400" />
                {selectedStock.name} ({selectedStock.symbol})
              </h2>
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span>当前价格:</span>
                  <span className="font-mono text-lg text-green-400">
                    ¥{selectedStock.current_price?.toFixed(2)}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span>技术评分:</span>
                  <span className="font-mono">{selectedStock.technical_score}/10</span>
                </div>
                <div className="flex justify-between">
                  <span>基本面评分:</span>
                  <span className="font-mono">{selectedStock.fundamental_score}/10</span>
                </div>
                <div className="flex justify-between">
                  <span>综合评分:</span>
                  <span className="font-mono text-yellow-400">{selectedStock.total_score}/20</span>
                </div>
              </div>
            </div>

            {/* 技术指标卡片 */}
            <div className="bg-gray-800 rounded-lg p-6">
              <h3 className="text-lg font-bold mb-4">关键技术指标</h3>
              <div className="space-y-3">
                <div className="flex justify-between items-center">
                  <span>RSI (14):</span>
                  <div className="text-right">
                    <span className="font-mono">{indicators.rsi?.value}</span>
                    <div className={`text-sm ${indicators.rsi?.color}`}>
                      {indicators.rsi?.signal} - {indicators.rsi?.advice}
                    </div>
                  </div>
                </div>
                <div className="flex justify-between items-center">
                  <span>市盈率:</span>
                  <div className="text-right">
                    <span className="font-mono">{indicators.pe?.value}</span>
                    <div className={`text-sm ${indicators.pe?.color}`}>{indicators.pe?.signal}</div>
                  </div>
                </div>
                <div className="flex justify-between items-center">
                  <span>市净率:</span>
                  <div className="text-right">
                    <span className="font-mono">{indicators.pb?.value}</span>
                    <div className={`text-sm ${indicators.pb?.color}`}>{indicators.pb?.signal}</div>
                  </div>
                </div>
                <div className="flex justify-between items-center">
                  <span>ROE:</span>
                  <div className="text-right">
                    <span className="font-mono">{indicators.roe?.value}</span>
                    <div className={`text-sm ${indicators.roe?.color}`}>{indicators.roe?.signal}</div>
                  </div>
                </div>
                <div className="flex justify-between items-center">
                  <span>最大回撤:</span>
                  <div className="text-right">
                    <span className="font-mono">{indicators.drawdown?.value}</span>
                    <div className={`text-sm ${indicators.drawdown?.color}`}>{indicators.drawdown?.signal}</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {analysisView === 'technical' && (
          <div className="bg-gray-800 rounded-lg p-6">
            <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
              <TrendingUp className="text-blue-400" />
              技术面分析
            </h2>
            {report.technical.length > 0 ? (
              <div className="space-y-2">
                {report.technical.map((reason, index) => (
                  <div key={index} className="flex items-center gap-2 p-2 bg-gray-700 rounded">
                    <AlertTriangle className="w-4 h-4 text-yellow-400" />
                    <span>{reason}</span>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-gray-400">暂无技术面分析数据</p>
            )}
          </div>
        )}

        {analysisView === 'fundamental' && (
          <div className="bg-gray-800 rounded-lg p-6">
            <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
              <PieChart className="text-green-400" />
              基本面分析
            </h2>
            {report.fundamental.length > 0 ? (
              <div className="space-y-2">
                {report.fundamental.map((reason, index) => (
                  <div key={index} className="flex items-center gap-2 p-2 bg-gray-700 rounded">
                    <TrendingUp className="w-4 h-4 text-green-400" />
                    <span>{reason}</span>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-gray-400">暂无基本面分析数据</p>
            )}
          </div>
        )}

        {analysisView === 'charts' && (
          <div className="space-y-6">
            {/* RSI图表 */}
            <div className="bg-gray-800 rounded-lg p-6">
              <h3 className="text-lg font-bold mb-4">RSI相对强弱指标对比</h3>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={rsiData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                  <XAxis dataKey="name" stroke="#9CA3AF" />
                  <YAxis stroke="#9CA3AF" />
                  <Tooltip 
                    contentStyle={{ 
                      backgroundColor: '#1F2937', 
                      border: '1px solid #374151',
                      color: '#F3F4F6'
                    }} 
                  />
                  <Legend />
                  <Line type="monotone" dataKey="RSI" stroke="#60A5FA" strokeWidth={2} />
                  <Line type="monotone" dataKey="超买线" stroke="#EF4444" strokeDasharray="5 5" />
                  <Line type="monotone" dataKey="超卖线" stroke="#10B981" strokeDasharray="5 5" />
                </LineChart>
              </ResponsiveContainer>
            </div>

            {/* 综合评分对比 */}
            <div className="bg-gray-800 rounded-lg p-6">
              <h3 className="text-lg font-bold mb-4">股票综合评分对比</h3>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                  <XAxis dataKey="name" stroke="#9CA3AF" />
                  <YAxis stroke="#9CA3AF" />
                  <Tooltip 
                    contentStyle={{ 
                      backgroundColor: '#1F2937', 
                      border: '1px solid #374151',
                      color: '#F3F4F6'
                    }} 
                  />
                  <Legend />
                  <Bar dataKey="技术评分" fill="#60A5FA" />
                  <Bar dataKey="基本面评分" fill="#10B981" />
                  <Bar dataKey="综合评分" fill="#F59E0B" />
                </BarChart>
              </ResponsiveContainer>
            </div>

            {/* PE-PB散点图 */}
            <div className="bg-gray-800 rounded-lg p-6">
              <h3 className="text-lg font-bold mb-4">PE-PB估值散点图</h3>
              <ResponsiveContainer width="100%" height={300}>
                <ScatterChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                  <XAxis dataKey="PE" stroke="#9CA3AF" name="PE" />
                  <YAxis dataKey="PB" stroke="#9CA3AF" name="PB" />
                  <Tooltip 
                    cursor={{ strokeDasharray: '3 3' }}
                    contentStyle={{ 
                      backgroundColor: '#1F2937', 
                      border: '1px solid #374151',
                      color: '#F3F4F6'
                    }} 
                  />
                  <Scatter dataKey="PE" fill="#8B5CF6" />
                </ScatterChart>
              </ResponsiveContainer>
            </div>
          </div>
        )}

        {/* 底部说明 */}
        <div className="mt-8 bg-gray-800 rounded-lg p-4 text-sm text-gray-400">
          <p>
            <strong>使用说明:</strong> 本工具提供白酒股票的技术指标分析，包括RSI、PE/PB比等关键指标。
            RSI &gt; 70为超买，&lt; 30为超卖；PE &lt; 15为低估，&gt; 25为高估。
            数据仅供参考，投资有风险，入市需谨慎。
          </p>
        </div>
      </div>
    </div>
  );
};

export default TechnicalAnalysisApp;