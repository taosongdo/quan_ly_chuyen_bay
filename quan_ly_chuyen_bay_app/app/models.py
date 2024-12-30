from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean, UniqueConstraint, Enum, Time, DECIMAL
from enum import Enum as AllEnum
from sqlalchemy.orm import relationship, backref
from flask_login import UserMixin
import hashlib
from app import db, app

class NganHang(db.Model):
    __tablename__ = "nganhang"
    id_ngan_hang = Column(Integer, autoincrement=True, primary_key=True)
    hinh_anh = Column(String(40), nullable=False)
    ten_ngan_hang = Column(String(40), nullable=False)
    ds_don_huy = relationship("DonHuy", backref="Ngan Hang", lazy=True)
    

class UserRole(AllEnum):
    QUAN_TRI = 1
    NHAN_VIEN = 2
    KHACH_HANG = 3


class SanBay(db.Model):
    __tablename__ = 'sanbay'
    id_san_bay = Column(Integer, autoincrement=True, primary_key=True)
    ten_san_bay = Column(String(20), nullable=False, unique=True)
    ds_san_bay_TG = relationship("SanBayTrungGian", backref="San bay", lazy=True)

    def __str__(self):
        return 'tên sân bay: ' + self.ten_san_bay


sanbay_tuyenbay = db.Table('sanbay_tuyenbay',
                           Column('id_san_bay_tuyen_bay', Integer, primary_key=True),
                           Column('id_san_bay', Integer, ForeignKey('sanbay.id_san_bay'), nullable=False),
                           Column('id_tuyen_bay', Integer, ForeignKey('tuyenbay.id_tuyen_bay'), nullable=False),
                           UniqueConstraint('id_san_bay', 'id_tuyen_bay', name='unique_sb_tb'),
                           )


class TuyenBay(db.Model):
    __tablename__ = 'tuyenbay'
    id_tuyen_bay = Column(Integer, autoincrement=True, primary_key=True)
    ten_tuyen_bay = Column(String(20), nullable=False, unique=True)
    ds_san_bay_tuyen_bay = relationship('SanBay', secondary='sanbay_tuyenbay', backref=backref('Tuyen Bay', lazy=True),
                                        cascade="all, delete")
    ds_chuyen_bay = relationship('ChuyenBay', backref='Tuyen Bay', lazy=True)
    hinh_anh = Column(String(30), nullable=False)

    def __str__(self):
        return 'tên tuyến bay: ' + self.ten_tuyen_bay


class MayBay(db.Model):
    __tablename__ = 'maybay'
    id_may_bay = Column(Integer, autoincrement=True, primary_key=True)
    ten_may_bay = Column(String(20), nullable=False)
    hang_may_bay = Column(String(20), nullable=False)
    ds_chuyen_bay = relationship("ChuyenBay", backref='May Bay', lazy=True)
    ds_ghe = relationship('Ghe', backref='MayBay', lazy=True)

    def __str__(self):
        return 'id máy bay: ' + str(self.id_may_bay) + ' - tên máy bay: ' + str(self.ten_may_bay)


class Ghe(db.Model):
    __tablename__ = 'ghe'
    id_ghe = Column(Integer, autoincrement=True, primary_key=True)
    id_may_bay = Column(Integer, ForeignKey('maybay.id_may_bay'), nullable=False)
    hang = Column(Integer, nullable=False)
    vi_tri = Column(Integer, nullable=False)
    ds_ve = relationship('Ve', backref="ghe", lazy=True)
    ds_don_huy = relationship('DonHuy', backref="ghe", lazy=True)
    __table_args__ = (
        UniqueConstraint('id_may_bay', 'vi_tri', 'hang', name='unique_id_may_bay_vi_tri_hang'),
    )

    def __str__(self):
        return 'id ghế: ' + str(self.id_ghe) + ' - hạng: ' + str(self.hang) + ' - vị trí: ' + str(
            self.vi_tri) + ' - ' + str(MayBay.query.filter(MayBay.id_may_bay == self.id_may_bay).first())


class QuyDinh(db.Model):
    __tablename__ = 'quydinh'
    id_quy_dinh = Column(Integer, autoincrement=True, primary_key=True)
    TG_bay_toi_thieu = Column(Time, nullable=False)
    SL_san_bay_toi_da = Column(Integer, nullable=False)
    TG_dung_toi_thieu = Column(Time, nullable=False)
    TG_dung_toi_da = Column(Time, nullable=False)
    TG_mua_truoc = Column(Time, nullable=False)
    TG_dat_truoc = Column(Time, nullable=False)
    ds_chuyen_bay = relationship('ChuyenBay', backref='Quy Dinh Chuyen Bay', lazy=True)
    ds_quy_dinh_hang_ve = relationship('QuyDinhHangVe', backref='Quy Dinh Chuyen Bay', lazy=True)

    def __str__(self):
        return 'id quy định: ' + str(self.id_quy_dinh)


class QuyDinhHangVe(db.Model):
    __tablename__ = "quydinhhangve"
    id_quy_dinh_hang_ve = Column(Integer, autoincrement=True, primary_key=True)
    id_quy_dinh = Column(Integer, ForeignKey('quydinh.id_quy_dinh'), nullable=False)
    hang = Column(Integer, nullable=False)
    don_gia = Column(DECIMAL, nullable=False)

    def __str__(self):
        return 'id quy định hạng vé: ' + str(self.id_quy_dinh_hang_ve) + ' - ' + str(
            QuyDinh.query.filter(QuyDinh.id_quy_dinh == self.id_quy_dinh).first())


class ChuyenBay(db.Model):
    __tablename__ = 'chuyenbay'
    id_chuyen_bay = Column(Integer, autoincrement=True, primary_key=True)
    id_may_bay = Column(Integer, ForeignKey('maybay.id_may_bay'), nullable=False)
    id_tuyen_bay = Column(Integer, ForeignKey("tuyenbay.id_tuyen_bay"), nullable=False)
    id_quy_dinh = Column(Integer, ForeignKey('quydinh.id_quy_dinh'), nullable=False)
    ds_ve = relationship('Ve', backref='Chuyen Bay', lazy=True)
    id_lich_chuyen_bay = relationship("LichChuyenBay", backref='Chuyen Bay', lazy=True, uselist=False)
    ds_don_huy = relationship("DonHuy", backref="Chuyen Bay", lazy=True)

    def __str__(self):
        return 'id chuyến bay: ' + str(self.id_chuyen_bay) + ' - ' + str(
            TuyenBay.query.filter(TuyenBay.id_tuyen_bay == self.id_tuyen_bay).first())


class SanBayTrungGian(db.Model):
    __tablename__ = 'sanbaytrunggian'
    id_san_bay_trung_gian = Column(Integer, autoincrement=True, primary_key=True)
    id_san_bay = Column(Integer, ForeignKey('sanbay.id_san_bay'), nullable=False)
    id_lich_chuyen_bay = Column(Integer, ForeignKey('lichchuyenbay.id_chuyen_bay'), nullable=False)
    thoi_gian_dung = Column(Time)
    ghi_chu = Column(String(20))
    __table_args__ = (
        UniqueConstraint('id_san_bay', 'id_lich_chuyen_bay', name="unique_id_san_bay_id_lich_chuyen_bay"),
    )


class LichChuyenBay(db.Model):
    __tablename__ = 'lichchuyenbay'
    id_chuyen_bay = Column(Integer, ForeignKey('chuyenbay.id_chuyen_bay'), primary_key=True)
    ngay_gio = Column(DateTime, nullable=False)
    thoi_gian_bay = Column(Time, nullable=False)
    ds_san_bay = relationship("SanBayTrungGian", backref='Lich Chuyen Bay', lazy=True)

    def __str__(self):
        return 'id lịch chuyến bay: ' + str(self.id_chuyen_bay) + " - " + str(
            ChuyenBay.query.filter(ChuyenBay.id_chuyen_bay == self.id_chuyen_bay).first())


class NguoiDung(db.Model, UserMixin):
    __tablename__ = 'nguoidung'
    id_nguoi_dung = Column(Integer, autoincrement=True, primary_key=True)
    ten_nguoi_dung = Column(String(20), nullable=False)
    tai_khoan = Column(String(20), unique=True, nullable=False)
    mat_khau = Column(String(50))
    CCCD = Column(String(12), nullable=False, unique=True)
    gmail = Column(String(255), nullable=False, unique=True)
    user_role = Column(Enum(UserRole), default=UserRole.KHACH_HANG)
    hoat_dong = Column(Boolean, default=False)
    anh_dai_dien = Column(String(200))
    id_khach_hang = relationship('KhachHang', backref='nguoi dung', lazy=True, uselist=False)
    id_nhan_vien = relationship('NhanVien', backref='nguoi dung', lazy=True, uselist=False)
    ds_so_dien_thoai = relationship('SoDienThoai', backref='nguoi dung',lazy=True)
    
    def get_id(self):
        return self.id_nguoi_dung

    def __str__(self):
        return 'id người dùng: ' + str(self.id_nguoi_dung) + " - tên người dùng: " + str(
            self.ten_nguoi_dung) + " - loại: " + str(self.user_role)


class NhanVien(db.Model):
    __tablename__ = 'nhanvien'
    id_nhan_vien = Column(Integer, ForeignKey("nguoidung.id_nguoi_dung"), primary_key=True)
    ds_ve = relationship('Ve', backref='Nhan Vien', lazy=True)
    ds_don_huy = relationship("DonHuy", backref="Nhan Vien", lazy=True)

    def __str__(self):
        return 'id nhân viên: ' + str(self.id_nhan_vien) + ' ' + str(
            NguoiDung.query.filter(NguoiDung.id_nguoi_dung == self.id_nhan_vien).first())


class KhachHang(db.Model):
    __tablename__ = 'khachhang'
    id_khach_hang = Column(Integer, ForeignKey("nguoidung.id_nguoi_dung"), primary_key=True)
    ds_ve_mua = relationship('Ve', backref='Khach Hang', lazy=True)
    ds_don_huy = relationship('DonHuy', backref='Khach Hang', lazy=True)

    def __str__(self):
        return 'id khách hàng: ' + str(self.id_khach_hang) + ' ' + str(
            NguoiDung.query.filter(NguoiDung.id_nguoi_dung == self.id_khach_hang).first())


class Ve(db.Model):
    __tablename__ = 've'
    id_ve = Column(Integer, autoincrement=True, primary_key=True)
    id_khach_hang = Column(Integer, ForeignKey('khachhang.id_khach_hang'), nullable=False)
    id_chuyen_bay = Column(Integer, ForeignKey('chuyenbay.id_chuyen_bay'), nullable=False)
    id_nhan_vien = Column(Integer, ForeignKey('nhanvien.id_nhan_vien'))
    id_ghe = Column(Integer, ForeignKey('ghe.id_ghe'), nullable=False)
    hinh_thuc_thanh_toan = Column(Boolean)
    id_binh_luan = relationship("BinhLuan", backref="ve", uselist=False)
    __table_args__ = (
        UniqueConstraint('id_chuyen_bay', 'id_ghe', name='unique_id_chuyen_bay_id_ghe'),
    )

    def __str__(self):
        return 'id vé: ' + str(self.id_ve) + ' - ' + str(
            Ghe.query.filter(Ghe.id_ghe == self.id_ghe).first()) + ' - ' + str(
            ChuyenBay.query.filter(ChuyenBay.id_chuyen_bay == self.id_chuyen_bay).first())


class Muc(db.Model):
    id_muc = Column(Integer, autoincrement=True, primary_key=True)
    noi_dung = Column(String(40), nullable=False)
    href = Column(String(40), nullable=False)
    user_role = Column(Enum(UserRole), nullable=False)


class DonHuy(db.Model):
    __tablename__ = "donhuy"
    id_don_huy = Column(Integer, autoincrement=True, primary_key=True)
    id_khach_hang = Column(Integer, ForeignKey('khachhang.id_khach_hang'), nullable=False)
    id_chuyen_bay = Column(Integer, ForeignKey('chuyenbay.id_chuyen_bay'), nullable=False)
    id_nhan_vien = Column(Integer, ForeignKey('nhanvien.id_nhan_vien'))
    id_ghe = Column(Integer, ForeignKey('ghe.id_ghe'), nullable=False)
    id_ngan_hang = Column(Integer, ForeignKey("nganhang.id_ngan_hang"))
    so_tai_khoan = Column(String(16))
    __table_args__ = (
        UniqueConstraint('id_chuyen_bay', 'id_ghe', name='unique_id_chuyen_bay_id_ghe'),
    )


class BinhLuan(db.Model):
    __tablename__ = "binhluan"
    id_binh_luan = Column(Integer, ForeignKey('ve.id_ve'), primary_key=True)
    noi_dung = Column(String(255), nullable=False)
    thoi_gian = Column(DateTime, nullable=False)


class SoDienThoai(db.Model):
    __tablename__ ="sodienthoai"
    id_so_dien_thoai = Column(Integer,primary_key=True,autoincrement=True)
    id_nguoi_dung = Column(Integer,ForeignKey('nguoidung.id_nguoi_dung'),nullable=False)
    so_dien_thoai = Column(String(10),nullable=False,unique=True)
    
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        nguoi_dung = NguoiDung(id_nguoi_dung=1,
                                ten_nguoi_dung="Lý Gia Tuấn",
                                mat_khau=str(hashlib.md5('lkjhg09876'.encode('utf-8')).hexdigest()),
                                tai_khoan="Tuan_QT",
                                CCCD="079204006573",
                                gmail="quantri@gmail.com",
                                user_role=UserRole.QUAN_TRI,
                                hoat_dong=True,
                                anh_dai_dien=None)
        db.session.add(nguoi_dung)
        
        ds_muc = [
            {
                "id_muc":1,
                "noi_dung":"đặt vé",
                "href": "/DatVe",
                "user_role": UserRole.KHACH_HANG,
            },
            {
                "id_muc":2,
                "noi_dung":"xem giỏ hàng",
                "href": "/XemGioHang",
                "user_role": UserRole.KHACH_HANG,
            },
            {
                "id_muc":3,
                "noi_dung":"quản lý lịch chuyến bay",
                "href": "/NhanVien/QuanLyLichChuyenBay",
                "user_role": UserRole.NHAN_VIEN,
            },
            {
                "id_muc":4,
                "noi_dung":"quản lý khách hàng",
                "href": "/NhanVien/QuanLyKhachHang",
                "user_role": UserRole.NHAN_VIEN,
            },
            {
                "id_muc":5,
                "noi_dung":"quản lý vé",
                "href": "/NhanVien/QuanLyVe",
                "user_role": UserRole.NHAN_VIEN,
            },
            {
                "id_muc":6,
                "noi_dung":"cập nhật đơn hủy",
                "href": "/NhanVien/XemDSDonHuy",
                "user_role": UserRole.NHAN_VIEN,
            }
        ]
        for muc in ds_muc:
            db.session.add(Muc(id_muc=muc["id_muc"],
                               noi_dung=muc["noi_dung"],
                               href=muc["href"],
                               user_role=muc["user_role"]))
        
        db.session.commit()
