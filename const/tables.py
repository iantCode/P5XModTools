from const.enums import Region

REGION_MAP = {
    Region.CN: {
        "exe_name": "P5X.exe",
        "launcher_folder": "P5XLaunch",
        "game_id": "1264",
        "launcher_version": "https://nsywl-client-dev1.wmupd.com/hd/P5XOB/launcher/Version.ini",
        "game_version": "https://nsywl-client-dev2.wmupd.com/clientRes/CN_OB_OFFICIAL/Version/Windows/config.xml",
        "res_list": "https://nsywl-client-dev1.wmupd.com/clientRes/CN_OB_OFFICIAL/Version/Windows/version/{}/ResList.zip",
        "res_url": "https://nsywl-client-dev1.wmupd.com/clientRes/CN_OB_OFFICIAL/Res",
        "hotfix_url": "https://nsywl-client.wmupd.com/hotfix/27/{}/{}/{}.json",
        "hotfix_base": "https://nsywl-client.wmupd.com/hotfix/27/",
        "reg_location": "SOFTWARE\\WOW6432Node\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\P5X"
    },
    Region.KR: {
        "exe_name": "P5XKORLauncher.exe",
        "launcher_folder": "P5XKOR",
        "game_id": "1000150",
        "launcher_version": "https://p5krcdn1.wmupd.com/hd/PWRDP5OB/launcher/Version.ini",
        "game_version": "https://p5krcdn1.wmupd.com/clientRes/KROB_offical_PC/Version/Windows/config.xml",
        "res_list": "https://p5krcdn1.wmupd.com/clientRes/KROB_offical_PC/Version/Windows/version/{}/ResList.zip",
        "res_url": "https://p5krcdn2.wmupd.com/clientRes/KROB_offical_PC/Res",
        "hotfix_url": "https://p5krcdn1.wmupd.com/clientRes/{}/hotfix/27/{}/{}/{}.json",
        "hotfix_base": "https://p5krcdn1.wmupd.com/clientRes/{}/hotfix/27/",
        "reg_location": "SOFTWARE\\WOW6432Node\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\P5XKO"
    },
    Region.TW: {
        "exe_name": "P5XGATLauncher.exe",
        "launcher_folder": "P5XGAT",
        "game_id": "2000005",
        "launcher_version": "https://patchp5x1.iwplay.com.tw/hd/IwplayP5OB/launcher/Version.ini",
        "game_version": "https://patchp5x1.iwplay.com.tw/clientRes/OB_offical_PC/Version/Windows/config.xml",
        "res_list": "https://patchp5x1.iwplay.com.tw/clientRes/OB_offical_PC/Version/Windows/version/{}/ResList.zip",
        "res_url": "https://patchp5x1.iwplay.com.tw/clientRes/OB_offical_PC/Res",
        "hotfix_url": "https://patchp5x1.iwplay.com.tw/clientRes/{}/hotfix/27/{}/{}/{}.json",
        "hotfix_base": "https://patchp5x1.iwplay.com.tw/clientRes/{}/hotfix/27/",
        "reg_location": "SOFTWARE\\WOW6432Node\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\P5XHMT"
    },
}

MOD_LINK = {
    Region.CN: "https://iant.kr/p5xmod/cnmod.zip",
    Region.KR: "https://iant.kr/p5xmod/krmod.zip",
    Region.TW: "https://iant.kr/p5xmod/twmod.zip"
}
