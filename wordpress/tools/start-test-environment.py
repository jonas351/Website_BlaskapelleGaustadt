#!/usr/bin/env python3
"""Local cloud test installation, never a deployment to the association's server."""
from pathlib import Path
import hashlib, json, secrets, subprocess, time, urllib.request, zipfile

REPO = Path(__file__).resolve().parents[2]
WORK = Path('/workspace/gaustadt-wp-test')
WP_IMAGE = 'wordpress@sha256:f32ffa85064d9c951b7b69c929fa2a9f682aa4443e0c0a56ac2000499cb64383'
DB_IMAGE = 'mariadb@sha256:1292844148b311e4ed4300022a996d39083f415a963e970cf47cad1b3b18e3a6'
ELEMENTOR_VERSION = '4.3.0'
ELEMENTOR_SHA256 = '35c359c81e76468ccee237d0a69b9fa3d4cc47095029ae49aa80724e9daf799a'

def run(args, capture=False):
    return subprocess.run(args,check=True,capture_output=capture,text=True)

def main():
    WORK.mkdir(parents=True,exist_ok=True)
    manifest = WORK / 'containers.json'
    owned = json.loads(manifest.read_text()) if manifest.exists() else {}
    names = {'db':'gaustadt-test-db','wp':'gaustadt-test-wp'}
    existing = {}
    for key,name in names.items():
        result=run(['docker','ps','-aq','--filter','name=^'+name+'$'],True).stdout.strip()
        if result:
            full=run(['docker','inspect','--format','{{.Id}}',name],True).stdout.strip()
            if owned.get(key) != full:
                raise SystemExit('Existing container is not owned by this helper: '+name)
            existing[key]=full
    if not (WORK/'db.env').exists():
        if existing: raise SystemExit('Local test credentials are missing; existing containers were left unchanged.')
        password=secrets.token_urlsafe(30)
        (WORK/'db.env').write_text('MARIADB_DATABASE=gaustadt\nMARIADB_USER=gaustadt\nMARIADB_PASSWORD='+password+'\nMARIADB_RANDOM_ROOT_PASSWORD=yes\n')
        (WORK/'wp.env').write_text('WORDPRESS_DB_HOST=gaustadt-test-db\nWORDPRESS_DB_NAME=gaustadt\nWORDPRESS_DB_USER=gaustadt\nWORDPRESS_DB_PASSWORD='+password+'\nGAUSTADT_TEST_ADMIN_PASS='+secrets.token_urlsafe(30)+'\nWORDPRESS_DEBUG=1\nWORDPRESS_CONFIG_EXTRA=define("WP_DEBUG_DISPLAY", false);define("WP_DEBUG_LOG", true);define("WP_HTTP_BLOCK_EXTERNAL", true);\n')
        for file in ('db.env','wp.env'): (WORK/file).chmod(0o600)
    if not (WORK/'wp.env').exists(): raise SystemExit('WordPress test credentials missing.')
    if subprocess.run(['docker','network','inspect','gaustadt-test-net'],capture_output=True).returncode:
        run(['docker','network','create','gaustadt-test-net'])
    for key,image in (('db',DB_IMAGE),('wp',WP_IMAGE)):
        if key in existing:
            run(['docker','start',names[key]],True)
            continue
        run(['docker','pull',image])
        args=['docker','run','-d','--name',names[key],'--network','gaustadt-test-net','--env-file',str(WORK/(key+'.env')),'--label','gaustadt.local-test=true']
        if key=='wp': args+=['-p','127.0.0.1:8088:80']
        result=run(args+[image],True)
        owned[key]=result.stdout.strip()
        manifest.write_text(json.dumps(owned,indent=2)+'\n')
    for _ in range(60):
        if subprocess.run(['docker','exec',names['db'],'healthcheck.sh','--connect','--innodb_initialized'],capture_output=True).returncode==0: break
        time.sleep(1)
    else: raise SystemExit('MariaDB did not become ready.')
    for _ in range(60):
        if subprocess.run(['docker','exec',names['wp'],'test','-f','/var/www/html/wp-load.php'],capture_output=True).returncode==0: break
        time.sleep(1)
    else: raise SystemExit('WordPress image did not initialize.')
    downloads=WORK/'downloads';downloads.mkdir(exist_ok=True)
    archive=downloads/('elementor-'+ELEMENTOR_VERSION+'.zip')
    if not archive.exists():
        url='https://github.com/elementor/elementor/releases/download/'+ELEMENTOR_VERSION+'/'+archive.name
        with urllib.request.urlopen(url,timeout=60) as response: archive.write_bytes(response.read())
    if hashlib.sha256(archive.read_bytes()).hexdigest()!=ELEMENTOR_SHA256:
        raise SystemExit('Elementor package checksum mismatch; package was not used.')
    with zipfile.ZipFile(archive) as z:
        for entry in z.infolist():
            if not (downloads/entry.filename).resolve().is_relative_to(downloads.resolve()): raise SystemExit('Unsafe ZIP path.')
        if z.testzip() is not None: raise SystemExit('Invalid Elementor ZIP.')
        z.extractall(downloads)
    run(['docker','exec',names['wp'],'mkdir','-p','/var/www/html/wp-content/plugins/elementor','/var/www/html/wp-content/themes/gaustadt-elementor'])
    run(['docker','cp',str(downloads/'elementor')+'/.',names['wp']+':/var/www/html/wp-content/plugins/elementor/'])
    theme=REPO/'wordpress/gaustadt-elementor'
    run(['docker','cp',str(theme)+'/.',names['wp']+':/var/www/html/wp-content/themes/gaustadt-elementor/'])
    run(['docker','exec',names['wp'],'sh','-c','find /var/www/html/wp-content/themes/gaustadt-elementor /var/www/html/wp-content/plugins/elementor -type d -exec chmod 755 {} + && find /var/www/html/wp-content/themes/gaustadt-elementor /var/www/html/wp-content/plugins/elementor -type f -exec chmod 644 {} +'])
    install='''<?php
$_SERVER['HTTP_HOST']='127.0.0.1:8088';$_SERVER['SERVER_SOFTWARE']='Apache';
define('WP_INSTALLING',true);
require '/var/www/html/wp-load.php';
require_once ABSPATH.'wp-admin/includes/upgrade.php';
require_once ABSPATH.'wp-admin/includes/plugin.php';
add_filter('pre_wp_mail','__return_true');
if(!is_blog_installed()){wp_install('Blaskapelle Gaustadt','gaustadt_test_admin','test@example.invalid',false,'',getenv('GAUSTADT_TEST_ADMIN_PASS'));}
update_option('home','http://127.0.0.1:8088');update_option('siteurl','http://127.0.0.1:8088');update_option('timezone_string','Europe/Berlin');update_option('blog_public',0);
$r=activate_plugin('elementor/elementor.php');if(is_wp_error($r)){throw new Exception($r->get_error_message());}switch_theme('gaustadt-elementor');
require_once ABSPATH.'wp-admin/includes/misc.php';require_once ABSPATH.'wp-admin/includes/file.php';
if(get_option('permalink_structure')===''){update_option('permalink_structure','/%postname%/');$GLOBALS['wp_rewrite']->init();flush_rewrite_rules(true);}
echo 'Local WordPress and Elementor ready.'.PHP_EOL;
'''
    (WORK/'install.php').write_text(install)
    run(['docker','cp',str(WORK/'install.php'),names['wp']+':/tmp/gaustadt-install.php'])
    run(['docker','exec',names['wp'],'php','/tmp/gaustadt-install.php'])
    print('Local test server ready on port 8088. Test credentials remain in '+str(WORK/'wp.env')+'; do not publish them.')

if __name__=='__main__': main()
