import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
L=module('ledger',ROOT/'shared/scripts/ledger.py')

class LedgerTests(unittest.TestCase):
    def setUp(self):
        self.c=L.read(ROOT/'shared/assets/config.example.json')
        self.a=L.read(ROOT/'tests/fixtures/mister-ads-publicidad-prueba.json')
        self.b=L.read(ROOT/'tests/fixtures/mister-ads-comercial-prueba.json')
        self.db={'schema_version':L.VERSION,'config':self.c,'revision':0,'opportunities':{},'payments':{},'reports':{},'history':[]}
        self.report,self.bundle=L.prototype(self.a,self.b,self.c)
    def seed(self):
        L.record(self.db,self.bundle);L.report_add(self.db,self.report)
    def test_fixture_totals_and_cohort(self):
        self.seed();s=L.summary(self.db,self.report['report_id'])
        self.assertEqual((s['opportunities'],s['won'],s['payments']),(5,2,7))
        self.assertEqual((s['agreed_won_minor'],s['gross_minor'],s['refunds_minor'],s['net_minor']),(20500000,17500000,1000000,16500000))
        self.assertEqual(s['unknown_origin'],1)
        self.assertEqual(s['advertising']['amount_spent_minor'],380500)
        self.assertEqual(len(s['advertising']['matched_cohort_opportunities']),4)
    def test_reimport_is_noop(self):
        self.seed();self.assertEqual(L.record(self.db,self.bundle),[]);self.assertEqual(L.report_add(self.db,self.report),[])
    def test_conflict_not_silent(self):
        self.seed();b=copy.deepcopy(self.bundle);b['opportunities'][0]['agreed_value_minor']=1
        with self.assertRaises(ValueError):L.record(self.db,b)
    def test_revision_has_before_after(self):
        self.seed();b=copy.deepcopy(self.bundle);b['opportunities'][0]['agreed_value_minor']=9000000
        changes=L.record(self.db,b,True)
        self.assertEqual(changes[0]['before']['agreed_value_minor'],8500000)
        self.assertEqual(changes[0]['after']['agreed_value_minor'],9000000)
    def test_report_id_conflict(self):
        self.seed();r=copy.deepcopy(self.report);r['rows'][0]['amount_spent_minor']=1
        with self.assertRaises(ValueError):L.report_add(self.db,r)
    def test_snapshots_not_summed(self):
        self.seed();r=copy.deepcopy(self.report);r['report_id']='another';L.report_add(self.db,r)
        self.assertEqual(L.summary(self.db,'another')['advertising']['amount_spent_minor'],380500)
    def test_missing_metrics_stay_unknown(self):
        self.report['rows'][0]['amount_spent_minor']=None;L.report_add(self.db,self.report)
        self.assertIsNone(L.summary(self.db,self.report['report_id'])['advertising']['amount_spent_minor'])
        self.assertIsNone(L.summary(self.db)['net_minor'])
    def test_currency_rejected(self):
        self.bundle['payments'][0]['currency']='USD'
        with self.assertRaises(ValueError):L.record(self.db,self.bundle)
    def test_business_rejected(self):
        self.bundle['business_id']='other'
        with self.assertRaises(ValueError):L.record(self.db,self.bundle)
    def test_real_and_synthetic_separated(self):
        self.report['synthetic']=False
        with self.assertRaises(ValueError):L.report_add(self.db,self.report)
    def test_refund_excess_rejected(self):
        self.bundle['payments'][4]['amount_minor']=5000001
        with self.assertRaises(ValueError):L.record(self.db,self.bundle)
    def test_refund_wrong_opportunity_rejected(self):
        self.bundle['payments'][4]['opportunity_id']='opp_test_01'
        with self.assertRaises(ValueError):L.record(self.db,self.bundle)
    def test_orphan_payment_rejected(self):
        self.bundle['payments'][0]['opportunity_id']='absent'
        with self.assertRaises(ValueError):L.record(self.db,self.bundle)
    def test_boolean_and_negative_amount_rejected(self):
        for value in (True,-1,1.5):
            with self.assertRaises(ValueError):L.number(value)
    def test_unknown_origin_kept(self):
        self.seed();o=self.db['opportunities']['opp_test_04']
        self.assertIsNone(o['ad_id']);self.assertIsNone(o['account_id'])
    def test_wrong_campaign_reported_as_conflict(self):
        self.bundle['opportunities'][0]['campaign_id']='wrong';self.seed()
        self.assertEqual(L.summary(self.db,self.report['report_id'])['advertising']['link_conflicts'],['opp_test_01'])
    def test_inconsistent_duplicate_rejected(self):
        self.bundle['opportunities'][-1]['status']='perdida'
        with self.assertRaises(ValueError):L.record(self.db,self.bundle)
    def test_dates_and_metadata(self):
        with self.assertRaises(ValueError):L.date('2026-02-30')
        self.report['generated_at']='2026-11-06T10:00:00'
        with self.assertRaises(ValueError):L.report_add(self.db,self.report)
    def test_json_duplicate_keys_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            p=Path(temp)/'bad.json';p.write_text('{"a":1,"a":2}')
            with self.assertRaises(ValueError):L.read(p)
    def test_cli_atomic_revision_lock_and_export(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)
            def run(*args):
                return subprocess.run([sys.executable,str(ROOT/'shared/scripts/ledger.py'),'--data-dir',temp,*args],capture_output=True,text=True,encoding='utf8')
            self.assertEqual(run('init','--config',str(ROOT/'shared/assets/config.example.json')).returncode,0)
            args=['import-prototype','--ads',str(ROOT/'tests/fixtures/mister-ads-publicidad-prueba.json'),'--commercial',str(ROOT/'tests/fixtures/mister-ads-comercial-prueba.json')]
            self.assertEqual(run(*args,'--expect-revision','0').returncode,0)
            old=(root/'ledger.json').read_bytes()
            self.assertNotEqual(run(*args,'--expect-revision','0').returncode,0)
            self.assertEqual((root/'ledger.json').read_bytes(),old)
            self.assertEqual(json.loads(run(*args,'--expect-revision','1').stdout)['status'],'unchanged')
            (root/'.ledger.lock').write_text('occupied')
            self.assertNotEqual(run(*args,'--expect-revision','1').returncode,0)
            self.assertEqual((root/'ledger.json').read_bytes(),old)
            (root/'.ledger.lock').unlink()
            bad=copy.deepcopy(self.bundle);bad['payments'][0]['amount_minor']=-1
            p=root/'bad.json';p.write_text(json.dumps(bad))
            self.assertNotEqual(run('record','--input',str(p),'--revise','--expect-revision','1').returncode,0)
            self.assertEqual((root/'ledger.json').read_bytes(),old)
            exported=json.loads(run('export').stdout)
            self.assertEqual(exported['revision'],1)
            self.assertEqual(len(exported['history']),1)

class PackageTests(unittest.TestCase):
    def test_install_and_refuse_overwrite(self):
        installer=module('installer',ROOT/'scripts/install.py')
        with tempfile.TemporaryDirectory() as temp:
            dest=installer.install(ROOT/'codex/skills/mister-ads',temp)
            self.assertTrue((dest/'engine/skills/ads-conciencia/SKILL.md').is_file())
            self.assertTrue((dest/'scripts/ledger.py').is_file())
            with self.assertRaises(ValueError):installer.install(ROOT/'codex/skills/mister-ads',temp)
    def test_editions_preserve_upstream_hashes(self):
        import hashlib
        lock=L.read(ROOT/'upstream.lock.json')
        for edition in ('codex','claude'):
            base=ROOT/edition/'skills/mister-ads'
            for name,sha in lock['files'].items():self.assertEqual(hashlib.sha256((base/'engine'/name).read_bytes()).hexdigest(),sha)
            for p in (ROOT/'shared').rglob('*'):
                if p.is_file() and '__pycache__' not in p.parts:self.assertEqual(p.read_bytes(),(base/p.relative_to(ROOT/'shared')).read_bytes())
    def test_engine_profile_isolation(self):
        with tempfile.TemporaryDirectory() as temp:
            script=ROOT/'codex/skills/mister-ads/scripts/engine_profile.py'
            cmd=[sys.executable,str(script),'--data-dir',temp,'--platform','meta','--account-id','act_demo']
            result=subprocess.run(cmd+['init'],capture_output=True,text=True)
            self.assertEqual(result.returncode,0,result.stderr)
            self.assertTrue((Path(temp)/'engine-profiles/meta-act_demo/profile.json').exists())
            wrong=Path(temp)/'wrong.json';wrong.write_text(json.dumps({'platform':'meta','account_id':'other'}))
            self.assertNotEqual(subprocess.run(cmd+['save-audit',str(wrong)],capture_output=True).returncode,0)

if __name__=='__main__':unittest.main()
