import os, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings'
import django; django.setup()

from predictions.future_predictor import get_top_recommendations
results = get_top_recommendations(min_score=48, max_results=10)
print(f"Got {len(results)} results")
for r in results:
    print(f"{r['symbol']:12s} {r['signal']:12s} score={r['composite_score']:5.1f} 3m={r['return_3m_pct']:+6.1f}% 6m={r['return_6m_pct']:+6.1f}%")
