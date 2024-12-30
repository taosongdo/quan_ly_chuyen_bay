from app import app, db
from flask_admin import Admin, BaseView, expose
from flask import redirect
from flask_admin.contrib.sqla import ModelView
from app.models import SanBay, TuyenBay, SanBayTrungGian, NhanVien, ChuyenBay, MayBay, Ghe, Ve, KhachHang, \
    NguoiDung, UserRole, LichChuyenBay, QuyDinhHangVe, QuyDinh, DonHuy,SoDienThoai

import hashlib
from datetime import datetime
from flask_login import current_user, logout_user

admin = Admin(app=app, name="admin", template_mode='bootstrap4')


class AuthenticatedModelView(ModelView):
    column_display_pk = True

    def is_accessible(self):
        return (current_user.is_authenticated and current_user.user_role == UserRole.QUAN_TRI)


class TuyenBayModelView(AuthenticatedModelView):
    column_list = ['id_tuyen_bay', 'ds_san_bay_tuyen_bay']

    def on_model_change(self, form, model, is_created):
        db.session.flush()
        if len(model.ds_san_bay_tuyen_bay) != 2:
            raise ValueError("Một tuyến bay bắt buộc có 2 sân bay")
        return super().on_model_change(form, model, is_created)


class QuyDinhHangVeModelView(AuthenticatedModelView):
    def on_model_change(self, form, model, is_created):
        db.session.flush()

        quy_dinh = QuyDinh.query.filter(QuyDinh.id_quy_dinh == model.id_quy_dinh).first()
        ds_chuyen_bay = quy_dinh.ds_chuyen_bay
        if len(ds_chuyen_bay) > 0:
            ds_may_bay = []
            for chuyen_bay in ds_chuyen_bay:
                may_bay = MayBay.query.filter(MayBay.id_may_bay == chuyen_bay.id_may_bay).first()
                ds_may_bay.append(may_bay)
            ds_may_bay = set(ds_may_bay)
            for may_bay in ds_may_bay:
                ds_ghe = Ghe.query.filter(Ghe.id_may_bay == may_bay.id_may_bay).all()
                check = False
                so_luong_ghe = 0
                for ghe in ds_ghe:
                    if ghe.hang == model.hang:
                        check = True
                        so_luong_ghe += 1
                if not (check):
                    raise ValueError("không có hạng ghế này")
        else:
            raise ValueError("chưa có chuyến bay nào")
        return super().on_model_change(form, model, is_created)


class SanBayTrungGianModelView(AuthenticatedModelView):
    def on_model_change(self, form, model, is_created):
        db.session.flush()

        lich_chuyen_bay = LichChuyenBay.query.filter(LichChuyenBay.id_chuyen_bay == model.id_lich_chuyen_bay).first()
        chuyen_bay = ChuyenBay.query.filter(ChuyenBay.id_chuyen_bay == lich_chuyen_bay.id_chuyen_bay).first()
        quy_dinh = QuyDinh.query.filter(QuyDinh.id_quy_dinh == chuyen_bay.id_quy_dinh).first()

        if not (quy_dinh.TG_dung_toi_thieu <= model.thoi_gian_dung and model.thoi_gian_dung <= quy_dinh.TG_dung_toi_da):
            raise ValueError("thời gian dừng không phù hợp với quy định")
        if len(lich_chuyen_bay.ds_san_bay) > quy_dinh.SL_san_bay_toi_da:
            raise ValueError("số lượng sân bay đã vượt mất quy định")

        tuyen_bay = TuyenBay.query.filter(TuyenBay.id_tuyen_bay == chuyen_bay.id_tuyen_bay).first()
        san_bay = SanBay.query.filter(SanBay.id_san_bay == model.id_san_bay).first()
        if tuyen_bay.ten_tuyen_bay.__contains__(san_bay.ten_san_bay):
            raise ValueError("sân bay này là điểm đi hoặc đến")
        return super().on_model_change(form, model, is_created)


class LichChuyenBayModelView(AuthenticatedModelView):
    def on_model_change(self, form, model, is_created):
        db.session.flush()
        chuyen_bay = ChuyenBay.query.filter(ChuyenBay.id_chuyen_bay == model.id_chuyen_bay).first()
        quy_dinh = QuyDinh.query.filter(QuyDinh.id_quy_dinh == chuyen_bay.id_quy_dinh).first()

        if model.thoi_gian_bay < quy_dinh.TG_bay_toi_thieu:
            raise ValueError("thời gian bay thấp hơn so với quy định")
        return super().on_model_change(form, model, is_created)

    def on_model_delete(self, model):
        chuyen_bay = ChuyenBay.query.filter(ChuyenBay.id_chuyen_bay == model.id_chuyen_bay).first()
        if len(chuyen_bay.ds_ve) != 0:
            raise ValueError("Chuyến bay đã có vé, không thế xóa")
        ds_san_bay_trung_gian = SanBayTrungGian.query.filter(
            SanBayTrungGian.id_lich_chuyen_bay == model.id_chuyen_bay).all()
        for san_bay_trung_gian in ds_san_bay_trung_gian:
            db.session.delete(san_bay_trung_gian)
        db.session.commit()
        return super().on_model_delete(model)


class VeModelView(AuthenticatedModelView):
    def on_model_change(self, form, model, is_created):
        db.session.flush()
        ghe = Ghe.query.filter(Ghe.id_ghe == model.id_ghe).first()
        lich_chuyen_bay = LichChuyenBay.query.filter(LichChuyenBay.id_chuyen_bay == model.id_chuyen_bay).first()
        if lich_chuyen_bay == None:
            raise ValueError("chuyến bay hiện tại chưa có lịch")
        return super().on_model_change(form, model, is_created)


class KhachHangModelView(AuthenticatedModelView):
    def on_model_change(self, form, model, is_created):
        db.session.flush()
        nguoi_dung = NguoiDung.query.filter(NguoiDung.id_nguoi_dung == model.id_khach_hang).first()
        if nguoi_dung.user_role != UserRole.KHACH_HANG:
            raise ValueError("không thể chọn người dùng khác ngoài khách hàng")
        return super().on_model_change(form, model, is_created)

    def on_model_delete(self, model):
        for ve in model.ds_ve:
            db.session.delete(ve)
        for don_huy in model.ds_don_huy:
            db.session.delete(don_huy)
        db.session.commit()
        return super().on_model_delete(model)


class NhanVienModelView(AuthenticatedModelView):
    def on_model_change(self, form, model, is_created):
        db.session.flush()
        nguoi_dung = NguoiDung.query.filter(NguoiDung.id_nguoi_dung == model.id_nhan_vien).first()
        if nguoi_dung.user_role != UserRole.NHAN_VIEN:
            raise ValueError("không thể chọn người dùng khác ngoài nhân viên")
        return super().on_model_change(form, model, is_created)


class NguoiDungModelView(AuthenticatedModelView):
    def on_model_change(self, form, model, is_created):
        model.mat_khau = str(hashlib.md5((model.mat_khau).encode('utf-8')).hexdigest())
        if model.anh_dai_dien == None:
            model.anh_dai_dien = "https://res.cloudinary.com/dx6brcofe/image/upload/v1733042485/nyigfvynduo2zs2swmxv.jpg"
        return super().on_model_change(form, model, is_created)


class ChuyenBayModelView(AuthenticatedModelView):
    def on_model_delete(self, model):
        for ve in model.ds_ve:
            db.session.delete(ve)
        db.session.commit()
        return super().on_model_delete(model)


class LogoutView(BaseView):
    @expose('/')
    def dang_xuat(self):
        logout_user()
        return redirect("/admin")

    def is_accessible(self):
        return (current_user.is_authenticated and current_user.user_role == UserRole.QUAN_TRI)


class ChartView(BaseView):
    @expose('/')
    def index(self):
        nam = datetime.now().year
        return self.render("admin/XemBaoCao.html", nam=nam)

    def is_accessible(self):
        return (current_user.is_authenticated and current_user.user_role == UserRole.QUAN_TRI)


admin.add_view(AuthenticatedModelView(SanBay, db.session, name="sân bay"))
admin.add_view(TuyenBayModelView(TuyenBay, db.session, name="tuyến bay"))
admin.add_view(AuthenticatedModelView(MayBay, db.session, name="máy bay"))
admin.add_view(AuthenticatedModelView(Ghe, db.session, name="ghế"))
admin.add_view(AuthenticatedModelView(QuyDinh, db.session, "quy định"))
admin.add_view(QuyDinhHangVeModelView(QuyDinhHangVe, db.session, name="quy định hạng vé"))
admin.add_view(ChuyenBayModelView(ChuyenBay, db.session, name="chuyến bay"))
admin.add_view(SanBayTrungGianModelView(SanBayTrungGian, db.session, name="sân bay trung gian"))
admin.add_view(LichChuyenBayModelView(LichChuyenBay, db.session, name="lịch chuyến bay"))
admin.add_view(AuthenticatedModelView(SoDienThoai, db.session, name="số điện thoại"))

admin.add_view(NguoiDungModelView(NguoiDung, db.session, name="người dùng"))
admin.add_view(NhanVienModelView(NhanVien, db.session, name="nhân viên"))
admin.add_view(KhachHangModelView(KhachHang, db.session, name="khách hàng"))

admin.add_view(VeModelView(Ve, db.session, name="vé"))
admin.add_view(AuthenticatedModelView(DonHuy, db.session, name="đơn hủy"))

admin.add_view(ChartView(name="xem báo cáo"))
admin.add_view(LogoutView(name="thoát"))
