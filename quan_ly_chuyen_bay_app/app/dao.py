from app.models import SanBay, TuyenBay, SanBayTrungGian, NhanVien, ChuyenBay, MayBay, Ghe, Ve, KhachHang, db, \
    NguoiDung, LichChuyenBay, UserRole, QuyDinh, QuyDinhHangVe, sanbay_tuyenbay, Muc, DonHuy, NganHang, BinhLuan,\
    SoDienThoai
from datetime import datetime
from sqlalchemy.sql import or_
from sqlalchemy import func
from sqlalchemy.orm import aliased
import hashlib
import cloudinary.uploader
from app import app


# tuyen_bay
def lay_ds_tuyen_bay(trang=None, ten_tuyen_bay=None):
    ds_tuyen_bay = TuyenBay.query
    if trang:
        page_size = app.config['PAGE_SIZE']
        bat_dau = (trang - 1) * page_size
        ds_tuyen_bay = ds_tuyen_bay.slice(bat_dau, bat_dau + page_size)
    if ten_tuyen_bay:
        ds_tuyen_bay = ds_tuyen_bay.filter(TuyenBay.ten_tuyen_bay.contains(ten_tuyen_bay))
    return ds_tuyen_bay.all()


def lay_tuyen_bay_theo_id(id_tuyen_bay):
    return TuyenBay.query.filter(TuyenBay.id_tuyen_bay == id_tuyen_bay).first()


def dem_so_luong_tuyen_bay():
    return TuyenBay.query.count()


def lay_dict_tuyen_bay_theo_chuyen_bay():
    ds_tuyen_bay = {}
    ds_chuyen_bay = ChuyenBay.query.all()
    for chuyen_bay in ds_chuyen_bay:
        ds_tuyen_bay[chuyen_bay] = TuyenBay.query.filter(TuyenBay.id_tuyen_bay == chuyen_bay.id_tuyen_bay).first()
    return ds_tuyen_bay


# nguoi_dung
def lay_nguoi_dung_theo_id(id_nguoi_dung):
    return NguoiDung.query.filter(NguoiDung.id_nguoi_dung == id_nguoi_dung).first()


def kiem_tra_tai_khoan(tai_khoan, mat_khau, user_role):
    mat_khau = str(hashlib.md5(mat_khau.encode('utf-8')).hexdigest())
    return NguoiDung.query.filter((NguoiDung.tai_khoan == tai_khoan), (NguoiDung.mat_khau == mat_khau),
                                  (NguoiDung.user_role == user_role), (NguoiDung.hoat_dong == True)).first()


def tao_nguoi_dung_moi(ten_nguoi_dung, CCCD, gmail, tai_khoan, mat_khau, hoat_dong, anh_dai_dien):
    try:
        if hoat_dong:
            nguoi_dung = NguoiDung(ten_nguoi_dung=ten_nguoi_dung, CCCD=CCCD, gmail=gmail, tai_khoan=tai_khoan, mat_khau=str(hashlib.md5(mat_khau.encode('utf-8')).hexdigest()),
                                   user_role=UserRole.KHACH_HANG, hoat_dong=hoat_dong)
        else:
            nguoi_dung = NguoiDung(ten_nguoi_dung=ten_nguoi_dung, CCCD=CCCD, gmail=gmail,
                                   tai_khoan=tai_khoan, mat_khau=None, user_role=UserRole.KHACH_HANG,
                                   hoat_dong=hoat_dong)
        db.session.add(nguoi_dung)
        db.session.commit()
        khach_hang = KhachHang(id_khach_hang=nguoi_dung.id_nguoi_dung)
        db.session.add(khach_hang)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        nguoi_dung = NguoiDung.query.filter(NguoiDung.CCCD == CCCD, NguoiDung.gmail,
                                            NguoiDung.hoat_dong == False).first()
        if nguoi_dung and not (nguoi_dung.hoat_dong) and hoat_dong:
            nguoi_dung.ten_nguoi_dung = ten_nguoi_dung
            nguoi_dung.tai_khoan = tai_khoan
            nguoi_dung.mat_khau = str(hashlib.md5(mat_khau.encode('utf-8')).hexdigest())
            nguoi_dung.hoat_dong = True
            if anh_dai_dien:
                res = cloudinary.uploader.upload(anh_dai_dien)
                nguoi_dung.anh_dai_dien = res['secure_url']
            else:
                nguoi_dung.anh_dai_dien = "https://res.cloudinary.com/dx6brcofe/image/upload/v1733042485/nyigfvynduo2zs2swmxv.jpg"
            db.session.commit()
            return nguoi_dung
        else:
            print(e)
            return None
    else:
        if anh_dai_dien:
            res = cloudinary.uploader.upload(anh_dai_dien)
            nguoi_dung.anh_dai_dien = res['secure_url']
        else:
            nguoi_dung.anh_dai_dien = "https://res.cloudinary.com/dx6brcofe/image/upload/v1733042485/nyigfvynduo2zs2swmxv.jpg"
        db.session.commit()
        return nguoi_dung


def lay_nguoi_dung_theo_id_login(id_nguoi_dung):
    return NguoiDung.query.filter(NguoiDung.id_nguoi_dung == id_nguoi_dung, NguoiDung.hoat_dong == True).first()


def xoa_nguoi_dung_theo_id(id_nguoi_dung):
    nguoi_dung = NguoiDung.query.filter(NguoiDung.id_nguoi_dung == id_nguoi_dung).first()
    db.session.delete(nguoi_dung)
    db.session.commit()


def sua_nguoi_dung(id_nguoi_dung =None,gmail=None, tai_khoan=None, ten_nguoi_dung=None, CCCD=None, mat_khau=None, hoat_dong = True, anh_dai_dien=None):
    try:
        nguoi_dung = NguoiDung.query.filter(NguoiDung.id_nguoi_dung == id_nguoi_dung).first()
        if ten_nguoi_dung:
            nguoi_dung.ten_nguoi_dung = ten_nguoi_dung
        if CCCD:
            nguoi_dung.CCCD = CCCD
        if mat_khau and mat_khau != "":
            nguoi_dung.mat_khau = str(hashlib.md5(mat_khau.encode('utf-8')).hexdigest())
        nguoi_dung.hoat_dong = hoat_dong
        if tai_khoan:
            nguoi_dung.tai_khoan = tai_khoan
        if anh_dai_dien:
            res = cloudinary.uploader.upload(anh_dai_dien)
            nguoi_dung.anh_dai_dien = res['secure_url']
        if gmail:
            nguoi_dung.gmail = gmail
        db.session.commit()
    except:
        db.session.rollback()
        return None
    else:
        return nguoi_dung

def lay_nguoi_dung_ki_cang(gmail,tai_khoan, CCCD, user_role):
    ds_nguoi_dung = NguoiDung.query
    ds_nguoi_dung = ds_nguoi_dung.filter(NguoiDung.tai_khoan == tai_khoan)
    ds_nguoi_dung = ds_nguoi_dung.filter(NguoiDung.gmail == gmail)
    ds_nguoi_dung = ds_nguoi_dung.filter(NguoiDung.CCCD == CCCD)
    ds_nguoi_dung = ds_nguoi_dung.filter(NguoiDung.user_role == user_role)
    ds_nguoi_dung = ds_nguoi_dung.first()
    return ds_nguoi_dung

def lay_ds_nguoi_dung(gmail = None,tai_khoan=None, CCCD=None, user_role=None):
    ds_nguoi_dung = NguoiDung.query
    if tai_khoan:
        ds_nguoi_dung = ds_nguoi_dung.filter(NguoiDung.tai_khoan == tai_khoan)
    if gmail:
        ds_nguoi_dung = ds_nguoi_dung.filter(NguoiDung.gmail.ilike(f"%{gmail}%"))
    if CCCD:
        ds_nguoi_dung = ds_nguoi_dung.filter(NguoiDung.CCCD.ilike(f"%{CCCD}%"))
    if user_role:
        ds_nguoi_dung = ds_nguoi_dung.filter(NguoiDung.user_role == user_role)
    ds_nguoi_dung = ds_nguoi_dung.all()
    return ds_nguoi_dung


# chuyen_bay
def tra_cuu_chuyen_bay(id_chuyen_bay=None, id_tuyen_bay=None, ngay_gio=None, check=None):
    ds_chuyen_bay = db.session.query(ChuyenBay, TuyenBay, LichChuyenBay, QuyDinh, MayBay) \
        .join(TuyenBay, TuyenBay.id_tuyen_bay == ChuyenBay.id_tuyen_bay) \
        .join(MayBay, MayBay.id_may_bay == ChuyenBay.id_may_bay) \
        .join(QuyDinh, QuyDinh.id_quy_dinh == ChuyenBay.id_quy_dinh) \
        .join(LichChuyenBay, LichChuyenBay.id_chuyen_bay == ChuyenBay.id_chuyen_bay, isouter=True)

    if id_chuyen_bay:
        ds_chuyen_bay = ds_chuyen_bay.filter(ChuyenBay.id_chuyen_bay == id_chuyen_bay)

    if id_tuyen_bay:
        ds_chuyen_bay = ds_chuyen_bay.filter(TuyenBay.id_tuyen_bay == id_tuyen_bay)

    if ngay_gio:
        ds_chuyen_bay = ds_chuyen_bay.filter(LichChuyenBay.ngay_gio.ilike(f"%{ngay_gio}%"))

    if check == 1:
        ds_chuyen_bay = ds_chuyen_bay.filter(LichChuyenBay.ngay_gio >= (func.now() + QuyDinh.TG_dat_truoc))
    elif check == 2:
        ds_chuyen_bay = ds_chuyen_bay.filter(LichChuyenBay.id_chuyen_bay == None)
    elif check == 3:
        ds_chuyen_bay = ds_chuyen_bay.filter(LichChuyenBay.ngay_gio >= (func.now() + QuyDinh.TG_mua_truoc))

    return ds_chuyen_bay.all()


def lay_chuyen_bay_theo_id(id_chuyen_bay):
    return ChuyenBay.query.filter(ChuyenBay.id_chuyen_bay == id_chuyen_bay).first()


# khach_hang
def xoa_khach_hang_theo_id(id_khach_hang):
    ds_ve = Ve.query.filter(Ve.id_khach_hang == id_khach_hang).all()
    ds_don_huy = DonHuy.query.filter(DonHuy.id_khach_hang == id_khach_hang).all()
    khach_hang = db.session.query(KhachHang).filter(KhachHang.id_khach_hang == id_khach_hang).first()
    db.session.delete(khach_hang)
    for ve in ds_ve:
        db.session.delete(ve)
    for don_huy in ds_don_huy:
        db.session.delete(don_huy)
    db.session.commit()


# ghe
def lay_ds_ghe(id_chuyen_bay=None):
    ds_ghe = db.session.query(Ghe, MayBay, TuyenBay, ChuyenBay) \
        .join(Ghe, Ghe.id_may_bay == MayBay.id_may_bay) \
        .join(ChuyenBay, ChuyenBay.id_may_bay == MayBay.id_may_bay) \
        .join(TuyenBay, TuyenBay.id_tuyen_bay == ChuyenBay.id_tuyen_bay)

    if id_chuyen_bay:
        ds_ghe = ds_ghe.filter(ChuyenBay.id_chuyen_bay == id_chuyen_bay)
    return ds_ghe.all()


def lay_ds_bang_ghe(ds_ghe):
    ds_bang = []
    so_luong = len(ds_ghe)
    dem = 0
    hang = 1
    while dem < so_luong:
        table = []
        list = []
        a = 0
        for ghe in ds_ghe:
            if ghe.Ghe.hang == hang:
                list.append(ghe.Ghe)
                a += 1
                if a == 8:
                    a = 0
                    table.append(list)
                    dem += len(list)
                    list = []
        table.append(list)
        ds_bang.append(table)
        dem += len(list)
        hang += 1
    return ds_bang


# lich_chuyen_bay
def chi_tiet_lich_chuyen_bay(id_chuyen_bay=None):
    ds_san_bay_trung_gian = db.session.query(ChuyenBay, LichChuyenBay, SanBayTrungGian, SanBay) \
        .join(LichChuyenBay, LichChuyenBay.id_chuyen_bay == ChuyenBay.id_chuyen_bay) \
        .join(SanBayTrungGian, SanBayTrungGian.id_lich_chuyen_bay == LichChuyenBay.id_chuyen_bay, isouter=True) \
        .join(SanBay, SanBay.id_san_bay == SanBayTrungGian.id_san_bay, isouter=True)

    if id_chuyen_bay:
        ds_san_bay_trung_gian = ds_san_bay_trung_gian.filter(LichChuyenBay.id_chuyen_bay == id_chuyen_bay)

    return ds_san_bay_trung_gian.all()


def tao_lich_chuyen_bay(id_chuyen_bay, ngay_gio, thoi_gian_bay):
    try:
        lich_chuyen_bay = LichChuyenBay(id_chuyen_bay=id_chuyen_bay, ngay_gio=ngay_gio, thoi_gian_bay=thoi_gian_bay)
        db.session.add(lich_chuyen_bay)
        db.session.commit()
    except:
        db.session.rollback()
        return None
    else:
        return lich_chuyen_bay


def xoa_lich_chuyen_bay(id_lich_chuyen_bay):
    lich_chuyen_bay = LichChuyenBay.query.filter(LichChuyenBay.id_chuyen_bay == id_lich_chuyen_bay).first()
    db.session.delete(lich_chuyen_bay)
    db.session.commit()


def sua_lich_chuyen_bay(id_lich_chuyen_bay, ngay_gio, thoi_gian_bay):
    try:
        lich_chuyen_bay = LichChuyenBay.query.filter(LichChuyenBay.id_chuyen_bay == id_lich_chuyen_bay).first()
        lich_chuyen_bay.ngay_gio = ngay_gio
        lich_chuyen_bay.thoi_gian_bay = thoi_gian_bay
        db.session.commit()
    except:
        return None
    else:
        return lich_chuyen_bay


def tra_cuu_lich_chuyen_bay(ngay_gio=None, ten_chuyen_bay=None):
    ds_lich_chuyen_bay = db.session.query(LichChuyenBay, ChuyenBay) \
        .join(ChuyenBay, LichChuyenBay.id_chuyen_bay == ChuyenBay.id_chuyen_bay) \
        .join(TuyenBay, TuyenBay.id_tuyen_bay == ChuyenBay.id_tuyen_bay)

    if ngay_gio:
        ds_lich_chuyen_bay = ds_lich_chuyen_bay.filter(LichChuyenBay.ngay_gio.ilike(f"%{ngay_gio}%"))

    if ten_chuyen_bay:
        ds_lich_chuyen_bay = ds_lich_chuyen_bay.filter(
            or_(TuyenBay.ten_tuyen_bay.like(f'%{ten_chuyen_bay}%'), ChuyenBay.id_chuyen_bay == ten_chuyen_bay))
    return ds_lich_chuyen_bay.all()


# quy_dinh
def lay_quy_dinh_theo_id(id_quy_dinh):
    return QuyDinh.query.filter(QuyDinh.id_quy_dinh == id_quy_dinh).first()


def kiem_tra_ngay_gio_theo_quy_dinh(quy_dinh, thoi_gian_dung):
    if thoi_gian_dung > quy_dinh.TG_dung_toi_thieu and thoi_gian_dung < quy_dinh.TG_dung_toi_da:
        return True
    return False


def kiem_tra_thoi_gian_bay_theo_quy_dinh(quy_dinh, thoi_gian_bay):
    if thoi_gian_bay < quy_dinh.TG_bay_toi_thieu:
        return False
    return True


# quy_dinh_hang_ve
def lay_quy_dinh_hang_ve(id_ghe=None):
    quy_dinh_hang_ve = db.session.query(QuyDinhHangVe, QuyDinh, ChuyenBay, MayBay, Ghe) \
        .join(QuyDinh, QuyDinh.id_quy_dinh == QuyDinhHangVe.id_quy_dinh) \
        .join(ChuyenBay, ChuyenBay.id_quy_dinh == QuyDinh.id_quy_dinh) \
        .join(MayBay, MayBay.id_may_bay == ChuyenBay.id_may_bay) \
        .join(Ghe, Ghe.id_may_bay == MayBay.id_may_bay)

    quy_dinh_hang_ve = quy_dinh_hang_ve.filter(QuyDinhHangVe.hang == Ghe.hang)

    if id_ghe:
        quy_dinh_hang_ve = quy_dinh_hang_ve.filter(Ghe.id_ghe == id_ghe)

    return quy_dinh_hang_ve.all()[0]


# don_dat_ve
def lay_ds_don_sau_khi_xoa(gio_hang, id_ghe):
    return {don['id_ghe']: don for don in (gio_hang.values()) if don['id_ghe'] != id_ghe}


def lay_ds_don(gio_hang, nguoi_dung):
    list = []
    if gio_hang:
        for don_hang in gio_hang.values():
            dict = {}
            chuyen_bay = lay_chuyen_bay_theo_id(don_hang['id_chuyen_bay'])

            id_ghe = don_hang['id_ghe']
            quy_dinh_hang_ve = lay_quy_dinh_hang_ve(id_ghe=id_ghe)
            gia_ban = quy_dinh_hang_ve.QuyDinhHangVe.don_gia
            dict['chuyen_bay'] = chuyen_bay
            dict['ten_nguoi_dung'] = nguoi_dung.ten_nguoi_dung
            dict['CCCD'] = nguoi_dung.CCCD
            dict['gmail'] = nguoi_dung.gmail
            dict['ghe'] = Ghe.query.filter(Ghe.id_ghe == id_ghe).first()
            dict['gia_ban'] = gia_ban
            list.append(dict)
    return list


# ve
def tra_cuu_ve(id_ve=None, ten_nguoi_dung=None, id_nguoi_dung=None, id_tuyen_bay=None, lich_su=False, all=False):
    nguoi_dung_nhan_vien = aliased(NguoiDung)
    ds_ve = db.session.query(Ve, KhachHang, NguoiDung, ChuyenBay, Ghe, NhanVien, MayBay, TuyenBay, LichChuyenBay,
                             nguoi_dung_nhan_vien.ten_nguoi_dung, BinhLuan) \
        .join(Ve, Ve.id_khach_hang == KhachHang.id_khach_hang) \
        .join(NguoiDung, NguoiDung.id_nguoi_dung == KhachHang.id_khach_hang) \
        .join(ChuyenBay, ChuyenBay.id_chuyen_bay == Ve.id_chuyen_bay) \
        .join(Ghe, Ghe.id_ghe == Ve.id_ghe) \
        .join(NhanVien, NhanVien.id_nhan_vien == Ve.id_nhan_vien, isouter=True) \
        .join(nguoi_dung_nhan_vien, nguoi_dung_nhan_vien.id_nguoi_dung == NhanVien.id_nhan_vien, isouter=True) \
        .join(MayBay, MayBay.id_may_bay == ChuyenBay.id_may_bay) \
        .join(TuyenBay, TuyenBay.id_tuyen_bay == ChuyenBay.id_tuyen_bay) \
        .join(LichChuyenBay, LichChuyenBay.id_chuyen_bay == ChuyenBay.id_chuyen_bay) \
        .join(BinhLuan, BinhLuan.id_binh_luan == Ve.id_ve, isouter=True)

    if id_ve:
        ds_ve = ds_ve.filter(Ve.id_ve == id_ve)
    if id_nguoi_dung:
        ds_ve = ds_ve.filter(NguoiDung.id_nguoi_dung == id_nguoi_dung)
    if ten_nguoi_dung:
        ds_ve = ds_ve.filter(NguoiDung.ten_nguoi_dung.ilike(f"%{ten_nguoi_dung}%"))
    if id_tuyen_bay:
        ds_ve = ds_ve.filter(TuyenBay.id_tuyen_bay == id_tuyen_bay)

    if not (all):
        if lich_su:
            ds_ve = ds_ve.filter(LichChuyenBay.ngay_gio < func.now())
        else:
            ds_ve = ds_ve.filter(LichChuyenBay.ngay_gio > func.now())

    return ds_ve.all()


def lay_dict_ve_theo_ghe_va_chuyen_bay():
    dict = {}
    ds_ghe = Ghe.query.all()
    ds_chuyen_bay = ChuyenBay.query.all()
    for ghe in ds_ghe:
        dict[ghe] = {}
        for chuyen_bay in ds_chuyen_bay:
            dict[ghe][chuyen_bay] = Ve.query.filter(Ve.id_chuyen_bay == chuyen_bay.id_chuyen_bay,
                                                    Ve.id_ghe == ghe.id_ghe).first()
    return dict


def tao_ve_moi(id_nguoi_dung, id_chuyen_bay, id_ghe, id_nhan_vien, hinh_thuc_thanh_toan):
    ve = Ve(id_khach_hang=id_nguoi_dung, id_chuyen_bay=id_chuyen_bay, id_ghe=id_ghe, id_nhan_vien=id_nhan_vien,
            hinh_thuc_thanh_toan=hinh_thuc_thanh_toan)
    db.session.add(ve)
    db.session.commit()


def xoa_ve_theo_id(id_ve):
    ve = Ve.query.filter(Ve.id_ve == id_ve).first()
    db.session.delete(ve)
    db.session.commit()


def cap_nhat_ve(id_ve, id_chuyen_bay, id_ghe, hinh_thuc_thanh_toan):
    ve = Ve.query.filter(Ve.id_ve == id_ve).first()
    ve.id_chuyen_bay = id_chuyen_bay
    ve.id_ghe = id_ghe
    ve.hinh_thuc_thanh_toan = hinh_thuc_thanh_toan
    db.session.commit()


# san_bay
def lay_ds_san_bay_con_lai(ds_id_san_bay,ten_san_bay = None):
    ds_san_bay = SanBay.query
    for id_san_bay in ds_id_san_bay:
        ds_san_bay = ds_san_bay.filter(SanBay.id_san_bay != id_san_bay)
        if ten_san_bay:
            ds_san_bay = ds_san_bay.filter(SanBay.ten_san_bay.ilike(f"%{ten_san_bay}%"))
    return ds_san_bay.all()


def lay_san_bay_theo_id(id_san_bay):
    return SanBay.query.filter(SanBay.id_san_bay == id_san_bay).first()


# kiem_tra_thoi_gian
def lay_thoi_gian(thoi_gian):
    try:
        thoi_gian = datetime.strptime(thoi_gian, "%H:%M:%S").time()
    except:
        return None
    else:
        return thoi_gian


def lay_ngay_gio(ngay_gio):
    try:
        ngay_gio = datetime.strptime(ngay_gio, "%Y-%m-%d %H:%M:%S")
    except:
        return None
    else:
        return ngay_gio


# san_bay_trung_gian
def tao_san_bay_trung_gian(id_san_bay, id_lich_chuyen_bay, thoi_gian_dung, ghi_chu):
    try:
        san_bay_trung_gian = SanBayTrungGian(id_san_bay=id_san_bay, id_lich_chuyen_bay=id_lich_chuyen_bay,
                                             thoi_gian_dung=thoi_gian_dung, ghi_chu=ghi_chu)
        db.session.add(san_bay_trung_gian)
        db.session.commit()
    except:
        db.session.rollback()
        return None
    else:
        return san_bay_trung_gian


def xoa_san_bay_trung_gian_theo_id_lich(id_lich_chuyen_bay):
    ds_san_bay_TG = SanBayTrungGian.query.filter(SanBayTrungGian.id_lich_chuyen_bay == id_lich_chuyen_bay).all()
    for san_bay_TG in ds_san_bay_TG:
        db.session.delete(san_bay_TG)
    db.session.commit()


def lay_ds_san_bay_trung_gian_theo_id_lich(id_lich_chuyen_bay):
    ds_san_bay_trung_gian_2 = []
    ds_san_bay_trung_gian = SanBayTrungGian.query.filter(SanBayTrungGian.id_lich_chuyen_bay == id_lich_chuyen_bay).all()
    for san_bay_trung_gian in ds_san_bay_trung_gian:
        ds_san_bay_trung_gian_2.append(SanBayTrungGian(id_san_bay_trung_gian=san_bay_trung_gian.id_san_bay_trung_gian
                                                       , id_lich_chuyen_bay=san_bay_trung_gian.id_lich_chuyen_bay
                                                       , id_san_bay=san_bay_trung_gian.id_san_bay
                                                       , thoi_gian_dung=san_bay_trung_gian.thoi_gian_dung
                                                       , ghi_chu=san_bay_trung_gian.ghi_chu))
    return ds_san_bay_trung_gian_2


def them_san_bay_trung_gian_theo_ds(ds_san_bay_trung_gian):
    for san_bay_trung_gian in ds_san_bay_trung_gian:
        db.session.add(san_bay_trung_gian)
    db.session.commit()


def lay_dict_san_bay_trung_gian_theo_san_bay(id_lich_chuyen_bay):
    dict = {}
    ds_san_bay = SanBay.query.all()
    for san_bay in ds_san_bay:
        dict[san_bay] = SanBayTrungGian.query.filter(SanBayTrungGian.id_san_bay == san_bay.id_san_bay,
                                                     SanBayTrungGian.id_lich_chuyen_bay == id_lich_chuyen_bay).first()
    return dict


# san_bay_tuyen_bay
def lay_ds_san_bay_tuyen_bay_theo_id_tuyen_bay(id_tuyen_bay):
    ds_sanbay_tuyenbay = list(db.session.query(sanbay_tuyenbay).all())
    ds_sanbay_tuyenbay_duoc_chon = []
    for pt_sanbay_tuyenbay in ds_sanbay_tuyenbay:
        if pt_sanbay_tuyenbay[2] == id_tuyen_bay:
            ds_sanbay_tuyenbay_duoc_chon.append(pt_sanbay_tuyenbay)
    return ds_sanbay_tuyenbay_duoc_chon


# muc
def lay_ds_muc_theo_user_role(user_role):
    return Muc.query.filter(Muc.user_role == user_role).all()


# don_huy
def tao_don_huy(id_khach_hang, id_chuyen_bay, id_nhan_vien, id_ghe, id_ngan_hang, so_tai_khoan):
    don_huy = DonHuy(id_nhan_vien=id_nhan_vien, id_ghe=id_ghe, id_ngan_hang=id_ngan_hang, id_khach_hang=id_khach_hang,
                     id_chuyen_bay=id_chuyen_bay, so_tai_khoan=so_tai_khoan)
    db.session.add(don_huy)
    db.session.commit()


def lay_ds_don_huy():
    ds_don_huy = db.session.query(DonHuy, Ghe, TuyenBay, ChuyenBay, KhachHang, NguoiDung, NganHang, NhanVien) \
        .join(Ghe, Ghe.id_ghe == DonHuy.id_ghe) \
        .join(ChuyenBay, ChuyenBay.id_chuyen_bay == DonHuy.id_chuyen_bay) \
        .join(TuyenBay, TuyenBay.id_tuyen_bay == ChuyenBay.id_tuyen_bay) \
        .join(KhachHang, KhachHang.id_khach_hang == DonHuy.id_khach_hang) \
        .join(NguoiDung, NguoiDung.id_nguoi_dung == KhachHang.id_khach_hang) \
        .join(NhanVien, NhanVien.id_nhan_vien == DonHuy.id_nhan_vien, isouter=True) \
        .join(NganHang, NganHang.id_ngan_hang == DonHuy.id_ngan_hang, isouter=True) \
        .all()
    return ds_don_huy


def sua_don_huy(id_don_huy, id_nhan_vien):
    don_huy = DonHuy.query.filter(DonHuy.id_don_huy == id_don_huy).first()
    don_huy.id_nhan_vien = int(id_nhan_vien)
    db.session.commit()


# ngan_hang
def lay_bang_ngan_hang():
    ds_ngan_hang = NganHang.query.all()
    hang = []
    bang = []
    dem = 0
    for ngan_hang in ds_ngan_hang:
        hang.append(ngan_hang)
        dem += 1
        if dem == 8:
            dem = 0
            bang.append(hang)
            hang = []
    bang.append(hang)
    return bang


# binh_luan
def them_binh_luan(id_ve, noi_dung):
    try:
        binh_luan = BinhLuan(id_binh_luan=id_ve, noi_dung=noi_dung, thoi_gian=datetime.now())
        db.session.add(binh_luan)
        db.session.commit()
    except:
        db.session.rollback()
        return None
    else:
        return binh_luan


# bao_cao_doanh_thu
def lay_du_lieu_bao_cao(thoi_gian='year', so=datetime.now().year, nam=datetime.now().year):
    ds_ten_tuyen_bay = [tuyen_bay.ten_tuyen_bay for tuyen_bay in lay_ds_tuyen_bay()]

    ds_so_luong_chuyen_bay = db.session.query(TuyenBay, func.count(ChuyenBay.id_chuyen_bay)) \
        .join(ChuyenBay, ChuyenBay.id_tuyen_bay == TuyenBay.id_tuyen_bay) \
        .join(LichChuyenBay, LichChuyenBay.id_chuyen_bay == ChuyenBay.id_chuyen_bay) \
        .filter(func.extract(thoi_gian, LichChuyenBay.ngay_gio) == so) \
        .filter(func.extract('year', LichChuyenBay.ngay_gio) == nam) \
        .group_by(TuyenBay).all()

    ds_so_luong_chuyen_bay_2 = {}
    for so_luong_chuyen_bay in ds_so_luong_chuyen_bay:
        ds_so_luong_chuyen_bay_2[so_luong_chuyen_bay[0].ten_tuyen_bay] = so_luong_chuyen_bay[1]

    ds_doanh_thu = db.session.query(TuyenBay, func.sum(QuyDinhHangVe.don_gia)) \
        .join(ChuyenBay, ChuyenBay.id_tuyen_bay == TuyenBay.id_tuyen_bay) \
        .join(LichChuyenBay, LichChuyenBay.id_chuyen_bay == ChuyenBay.id_chuyen_bay) \
        .join(QuyDinh, QuyDinh.id_quy_dinh == ChuyenBay.id_quy_dinh) \
        .join(QuyDinhHangVe, QuyDinhHangVe.id_quy_dinh == QuyDinh.id_quy_dinh) \
        .join(Ve, Ve.id_chuyen_bay == ChuyenBay.id_chuyen_bay, isouter=True) \
        .join(Ghe, Ghe.id_ghe == Ve.id_ghe, isouter=True) \
        .filter(func.extract(thoi_gian, LichChuyenBay.ngay_gio) == so) \
        .filter(func.extract('year', LichChuyenBay.ngay_gio) == nam) \
        .filter(Ghe.hang == QuyDinhHangVe.hang) \
        .group_by(TuyenBay) \
        .all()

    ds_doanh_thu_2 = {}
    for doanh_thu in ds_doanh_thu:
        ds_doanh_thu_2[doanh_thu[0].ten_tuyen_bay] = doanh_thu[1]

    return ds_ten_tuyen_bay, ds_so_luong_chuyen_bay_2, ds_doanh_thu_2

#so_dien_thoai
def tao_so_dien_thoai(id_nguoi_dung,so_dien_thoai):
    try:
        so_dien_thoai = SoDienThoai(id_nguoi_dung=id_nguoi_dung,so_dien_thoai=so_dien_thoai)
        db.session.add(so_dien_thoai)
        db.session.commit()
    except:
        db.session.rollback()
        return None
    else:
        return so_dien_thoai    

def lay_ds_so_dien_thoai(id_nguoi_dung):
    ds_so_dien_thoai = SoDienThoai.query.filter(SoDienThoai.id_nguoi_dung == id_nguoi_dung).all()
    ds_so_dien_thoai_2 = []
    for so_dien_thoai in ds_so_dien_thoai:
        ds_so_dien_thoai_2.append(SoDienThoai(id_so_dien_thoai=so_dien_thoai.id_so_dien_thoai,id_nguoi_dung=so_dien_thoai.id_nguoi_dung,so_dien_thoai=so_dien_thoai.so_dien_thoai)) 
    return ds_so_dien_thoai_2

def them_danh_sach_so_dien_thoai(ds_so_dien_thoai):
    for so_dien_thoai in ds_so_dien_thoai:
        db.session.add(SoDienThoai(id_so_dien_thoai=so_dien_thoai.id_so_dien_thoai,
                                   id_nguoi_dung = so_dien_thoai.id_nguoi_dung,
                                   so_dien_thoai = so_dien_thoai.so_dien_thoai))
    db.session.commit()
    
def xoa_so_dien_thoai(id_nguoi_dung):
    ds_so_dien_thoai = SoDienThoai.query.filter(SoDienThoai.id_nguoi_dung==id_nguoi_dung).all()
    for so_dien_thoai in ds_so_dien_thoai:
        db.session.delete(so_dien_thoai)
    db.session.commit()


def lay_ds_so_dien_thoai_theo_id_nguoi_dung(id_nguoi_dung):
    return SoDienThoai.query.filter(SoDienThoai.id_nguoi_dung == id_nguoi_dung).all()


def lay_so_luong_so_dien_thoai_theo_id_nguoi_dung(id_nguoi_dung):
    return SoDienThoai.query.filter(SoDienThoai.id_nguoi_dung == id_nguoi_dung).count()
if __name__ == '__main__':
    with app.app_context():
        pass
