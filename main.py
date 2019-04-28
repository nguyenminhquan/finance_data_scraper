from lib.scraper import BaoViet, VietStock, CafeF
import winsound

def vietstock():
    vs = VietStock()
    # vs.setSrc('test_stock_list')
    vs.setSrc('stock')
    vs.setPages(['1','2','3','4','5'])
    # vs.setPages(['1'])
    vs.startScraping()
    # vs.dowork('vfr')

def baoviet():

    bvTaget = {
        # 'ROA': 28
        # 'so_cp_luu_hanh_2': 2
        # 'tong_tai_san': 53
        # 'lai_chua_phan_phoi_2010': 86
        # 'lai_tu_hdkd': 11,
        'lai_rong_truoc_thue': 16,
        # 'lai_lo_thuan_sau_thue': 20
        'chi_phi_lai_vay': 8,
    }

    bv = BaoViet()
    # bv.setSrc('chuong')
    # bv.setSrc('test_stock_list')
    bv.setSrc('stock')
    bv.setOptions('1', '1', '1000000', '2018')
    bv.setTarget(bvTaget)
    bv.startScraping()
    # bv.dowork('vnm')


def cafef():
    cf = CafeF()
    cf.setSrc('stock')
    # cf.setSrc('test_stock_list')
    cf.setTarget(['DAR'])
    cf.startScraping()
    cf.export()

baoviet()

winsound.MessageBeep(winsound.MB_OK)
