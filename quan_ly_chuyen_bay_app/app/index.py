from flask import render_template, request, redirect, session, jsonify
from app.models import UserRole
from app import app, login
from flask_login import login_user, logout_user, current_user
import app.dao as dao
import app.utils as utils
import math
import app.vnpay as vnpay


@app.context_processor
def lay_thong_tin():
    if current_user.is_authenticated and current_user.user_role == UserRole.KHACH_HANG:
        return {
            "ds_muc": dao.lay_ds_muc_theo_user_role(UserRole.KHACH_HANG),
            "thong_tin": utils.lay_thong_tin(session.get("gio_hang"))
        }
    elif current_user.is_authenticated and current_user.user_role == UserRole.NHAN_VIEN:
        return {
            "ds_muc": dao.lay_ds_muc_theo_user_role(UserRole.NHAN_VIEN),
            "thong_tin": None
        }
    else:
        return {
            "ds_muc": [],
            "thong_tin": None
        }


@app.route("/TraCuuChuyenBay")
def tra_cuu_chuyen_bay():
    id_tuyen_bay = request.args.get("id_tuyen_bay") if request.args.get("id_tuyen_bay") != "None" else None
    ngay_gio = request.args.get("ngay_gio")
    link = request.args.get("link")
    link_chi_tiet = "/XemChiTietChuyenBay?link=/TraCuuChuyenBay"
    link_chi_tiet += ("?link=" + link + "&") if link else "&"
    check = 1
    if link:
        link = link.replace(";", "&")
        if link.__contains__("LapLichChuyenBay"):
            check = 2
        if link.__contains__("BanVe"):
            check = 3

    ds_chuyen_bay = dao.tra_cuu_chuyen_bay(id_tuyen_bay=id_tuyen_bay, ngay_gio=ngay_gio, check=check)
    ds_tuyen_bay = dao.lay_ds_tuyen_bay(trang=None, ten_tuyen_bay=None)
    return render_template("TraCuuChuyenBay.html", link_chi_tiet=link_chi_tiet, ds_tuyen_bay=ds_tuyen_bay,
                           ds_chuyen_bay=ds_chuyen_bay, link=link)


@app.route("/XemBinhLuan")
def xem_binh_luan():
    id_ve = request.args.get("id_ve")
    ds_ve = dao.tra_cuu_ve(lich_su=True)
    if id_ve:
        ve = dao.tra_cuu_ve(id_ve=id_ve, lich_su=True)[0]
    else:
        ve = None
    return render_template("KhachHang/XemBinhLuan.html", ds_ve=ds_ve, ve=ve)


@app.route("/XemChiTietChuyenBay")
def xem_chi_tiet_chuyen_bay():
    err = ""
    id_lich_chuyen_bay = int(request.args.get("id_lich_chuyen_bay"))
    chi_tiet_lich_chuyen_bay = dao.chi_tiet_lich_chuyen_bay(id_chuyen_bay=id_lich_chuyen_bay)
    link = request.args.get("link")
    return render_template("XemChiTietChuyenBay.html", err=err, link=link,
                           chi_tiet_lich_chuyen_bay=chi_tiet_lich_chuyen_bay)


#api
@app.route("/api/XoaDon/<id_ghe>", methods=['DELETE'])
def xoa_don(id_ghe):
    if current_user.is_authenticated and current_user.user_role == UserRole.KHACH_HANG:
        gio_hang = dict(session['gio_hang'])
        gio_hang = dao.lay_ds_don_sau_khi_xoa(gio_hang=gio_hang, id_ghe=id_ghe)
        session['gio_hang'] = gio_hang
        return jsonify(utils.lay_thong_tin(session['gio_hang']))


@app.route("/api/LayDuLieuBaoCao", methods=['POST'])
def lay_du_lieu_bao_cao():
    if current_user.is_authenticated and current_user.user_role == UserRole.QUAN_TRI:
        thoi_gian = request.json.get("thoi_gian")
        nam = request.json.get("nam")
        if thoi_gian == "tc":
            so = nam
            thoi_gian = 'year'
        elif thoi_gian.__contains__("q"):
            so = int(thoi_gian[1])
            thoi_gian = "quarter"
        else:
            so = int(thoi_gian[1:len(thoi_gian)])
            thoi_gian = "month"
        ds_ten_tuyen_bay, ds_so_luong_chuyen_bay, ds_doanh_thu = dao.lay_du_lieu_bao_cao(thoi_gian=thoi_gian, so=so,
                                                                                         nam=nam)
        data = {
            'ds_ten_tuyen_bay': ds_ten_tuyen_bay,
            'ds_luot_bay': ds_so_luong_chuyen_bay,
            'ds_doanh_thu': ds_doanh_thu
        }

        return jsonify(data)


@app.route("/api/ThemGioHang", methods=['POST'])
def them_gio_hang():
    if current_user.is_authenticated and current_user.user_role == UserRole.KHACH_HANG:
        if 'gio_hang' not in session:
            session['gio_hang'] = {}

        id_chuyen_bay = str(request.json.get('id_chuyen_bay'))
        id_ghe = str(request.json.get('id_ghe_chon'))

        gio_hang = dict(session['gio_hang'])
        gio_hang[id_ghe] = {
            'id_chuyen_bay': id_chuyen_bay,
            'id_ghe': id_ghe
        }
        session['gio_hang'] = gio_hang
        return jsonify(utils.lay_thong_tin(session['gio_hang']))


@app.route('/api/themBinhLuan/<int:id_ve>', methods=['POST'])
def them_binh_luan(id_ve):
    if current_user.is_authenticated and current_user.user_role == UserRole.KHACH_HANG:
        noi_dung = request.json.get('noiDung')
        binh_luan = dao.them_binh_luan(noi_dung=noi_dung, id_ve=id_ve)
        ve = dao.tra_cuu_ve(id_ve=id_ve, lich_su=True)[0]
        if binh_luan:
            return jsonify(
                {
                    "tuyen_bay": ve.TuyenBay.ten_tuyen_bay,
                    "noi_dung": ve.BinhLuan.noi_dung,
                    "thoi_gian": str(ve.BinhLuan.thoi_gian),
                    "nguoi_dung": {
                        "tai_khoan": ve.NguoiDung.tai_khoan,
                        "anh_dai_dien": ve.NguoiDung.anh_dai_dien
                    }
                })
        else:
            return jsonify({"loi": "bình luận cho vé này đã có"})


# khach_hang
@login.user_loader
def load_nguoi_dung(id_nguoi_dung):
    return dao.lay_nguoi_dung_theo_id_login(id_nguoi_dung=id_nguoi_dung)


@app.route("/QuenMatKhau", methods=["GET", "POST"])
def quen_mat_khau():
    if not (current_user.is_authenticated and current_user.user_role == UserRole.NHAN_VIEN):
        err = None
        xac_minh_gmail = request.args.get("xac_minh_gmail")
        xac_minh_gmail = None if xac_minh_gmail == "None" else xac_minh_gmail
        xac_minh_gmail = int(xac_minh_gmail) if xac_minh_gmail else None
        CCCD = None
        gmail = None
        tai_khoan = None
        if request.method == "POST":
            CCCD = request.form.get("CCCD")
            gmail = request.form.get("gmail")
            tai_khoan = request.form.get("tai_khoan").strip()
            nguoi_dung = dao.lay_nguoi_dung_ki_cang(CCCD=CCCD
                                                    , tai_khoan=tai_khoan
                                                    , user_role=UserRole.KHACH_HANG
                                                    , gmail=gmail)
            if nguoi_dung:
                if not (xac_minh_gmail):
                    session["ma_xac_minh_gmail"] = utils.gui_email(nguoi_dung.gmail)
                    xac_minh_gmail = 1
                else:
                    if xac_minh_gmail == 1:
                        ma_xac_minh = request.form.get("ma_xac_minh")
                        if ma_xac_minh != session["ma_xac_minh_gmail"]:
                            err = "mã xác minh không đúng"
                        else:
                            xac_minh_gmail = 2
                    else:
                        mat_khau = request.form.get("mat_khau")
                        xac_nhan = request.form.get("xac_nhan")
                        if mat_khau == xac_nhan:
                            dao.sua_nguoi_dung(id_nguoi_dung=nguoi_dung.id_nguoi_dung, mat_khau=mat_khau)
                            session["ma_xac_minh_gmail"] = None
                            return redirect("/DangNhap")
                        else:
                            err = "mật khẩu và xác nhận không giống nhau"
            else:
                err = "thông tin không chính xác"

        return render_template("KhachHang/QuenMatKhau.html"
                               , err=err
                               , xac_minh_gmail=xac_minh_gmail
                               , CCCD=CCCD
                               , gmail=gmail
                               , tai_khoan=tai_khoan)
    else:
        return redirect("/NhanVien")


@app.route("/DangKy", methods=["GET", "POST"])
def dang_ky():
    if not (current_user.is_authenticated and current_user.user_role == UserRole.NHAN_VIEN):
        sl_so_dien_thoai = request.args.get("sl_so_dien_thoai")
        if sl_so_dien_thoai and int(sl_so_dien_thoai) <= 3 and int(sl_so_dien_thoai) >= 1:
            sl_so_dien_thoai = int(sl_so_dien_thoai)
            err = None
            xac_minh_gmail = request.args.get("xac_minh_gmail")
            xac_minh_gmail = None if xac_minh_gmail == "None" else xac_minh_gmail
            ten_nguoi_dung = None
            CCCD = None
            gmail = None
            tai_khoan = None
            mat_khau = None
            xac_nhan = None
            anh_dai_dien = None
            ds_so_dien_thoai = []
            if request.method == "POST":
                ten_nguoi_dung = request.form.get("ten_nguoi_dung")
                CCCD = request.form.get("CCCD")
                gmail = request.form.get("gmail")
                tai_khoan = request.form.get("tai_khoan").strip()
                mat_khau = request.form.get("mat_khau").strip()
                xac_nhan = request.form.get("xac_nhan").strip()
                anh_dai_dien = request.files.get("anh_dai_dien")
                if mat_khau == xac_nhan:
                    nguoi_dung = dao.tao_nguoi_dung_moi(ten_nguoi_dung=ten_nguoi_dung,
                                                        CCCD=CCCD,
                                                        tai_khoan=tai_khoan, mat_khau=mat_khau, hoat_dong=True, gmail=gmail,
                                                        anh_dai_dien=anh_dai_dien)
                    if nguoi_dung:
                        kiem_tra = True
                        for so_dem in range(sl_so_dien_thoai):
                            so_dien_thoai = request.form.get("so_dien_thoai_"+str(so_dem))
                            if len(so_dien_thoai) == 10:
                                so_dien_thoai = dao.tao_so_dien_thoai(id_nguoi_dung=nguoi_dung.id_nguoi_dung,so_dien_thoai=so_dien_thoai)
                                if so_dien_thoai:
                                    dao.xoa_so_dien_thoai(id_nguoi_dung=nguoi_dung.id_nguoi_dung)
                                else:
                                    dao.xoa_khach_hang_theo_id(nguoi_dung.id_nguoi_dung)
                                    dao.xoa_nguoi_dung_theo_id(nguoi_dung.id_nguoi_dung)
                                    kiem_tra = False
                                    break
                            else:
                                dao.xoa_khach_hang_theo_id(nguoi_dung.id_nguoi_dung)
                                dao.xoa_nguoi_dung_theo_id(nguoi_dung.id_nguoi_dung)
                                kiem_tra = False
                                break
                        if kiem_tra:
                            if not (xac_minh_gmail):
                                dao.xoa_khach_hang_theo_id(nguoi_dung.id_nguoi_dung)
                                dao.xoa_nguoi_dung_theo_id(nguoi_dung.id_nguoi_dung)
                                session["ma_xac_minh_gmail"] = utils.gui_email(nguoi_dung.gmail)
                                xac_minh_gmail = True
                                
                                for so_dem in range(sl_so_dien_thoai):
                                    ds_so_dien_thoai.append(request.form.get("so_dien_thoai_"+str(so_dem)))
                                    
                            else:
                                ma_xac_minh = request.form.get("ma_xac_minh")
                                if ma_xac_minh != session["ma_xac_minh_gmail"]:
                                    dao.xoa_khach_hang_theo_id(nguoi_dung.id_nguoi_dung)
                                    dao.xoa_nguoi_dung_theo_id(nguoi_dung.id_nguoi_dung)
                                    err = "mã xác minh không đúng"
                                else:   
                                    for so_dem in range(sl_so_dien_thoai):
                                        dao.tao_so_dien_thoai(so_dien_thoai=request.form.get("so_dien_thoai_"+str(so_dem)),id_nguoi_dung=nguoi_dung.id_nguoi_dung)
                                    session["ma_xac_minh_gmail"] = None
                                    return redirect("/DangNhap")
                        else:
                            err="số điện thoại này đã được sử dụng"
                    else:
                        err = "thông tin đã được dùng để đăng ký"
                else:
                    err = "mật khẩu và xác nhận không giống nhau"

            return render_template("KhachHang/DangKy.html"
                                , err=err
                                , xac_minh_gmail=xac_minh_gmail
                                , ten_nguoi_dung=ten_nguoi_dung
                                , CCCD=CCCD
                                , gmail=gmail
                                , tai_khoan=tai_khoan
                                , mat_khau=mat_khau
                                , xac_nhan=xac_nhan
                                , anh_dai_dien=anh_dai_dien
                                , sl_so_dien_thoai=int(sl_so_dien_thoai)
                                , ds_so_dien_thoai=ds_so_dien_thoai)
        else:
             return redirect("/DangKy?sl_so_dien_thoai="+str(1))
    else:
        return redirect("/NhanVien")


@app.route("/DangNhap", methods=['GET', 'POST'])
def dang_nhap():
    if not (current_user.is_authenticated and current_user.user_role == UserRole.NHAN_VIEN):
        err = None
        link = request.args.get("link")
        if request.method == 'POST':
            tai_khoan = request.form.get("tai_khoan").strip()
            mat_khau = request.form.get("mat_khau").strip()
            khach_hang = dao.kiem_tra_tai_khoan(tai_khoan=tai_khoan, mat_khau=mat_khau, user_role=UserRole.KHACH_HANG)
            if khach_hang:
                login_user(khach_hang)
                if link:
                    return redirect(link)
                return redirect("/")
            else:
                err = "sai mật khẩu hoặc tài khoản"
        return render_template("KhachHang/DangNhap.html", err=err,link=link)
    else:
        return redirect("/NhanVien")


@app.route("/")
def trang_chu():
    if not (current_user.is_authenticated and current_user.user_role == UserRole.NHAN_VIEN):
        session['nguoi_dung'] = True
        trang = int(request.args.get("trang", 1))
        ds_tuyen_bay = dao.lay_ds_tuyen_bay(trang=trang, ten_tuyen_bay=None)
        so_luong_tuyen_bay = dao.dem_so_luong_tuyen_bay()
        page_size = app.config["PAGE_SIZE"]
        return render_template("KhachHang/TrangChu.html", ds_tuyen_bay=ds_tuyen_bay,
                               so_luong_trang=math.ceil(so_luong_tuyen_bay / page_size))
    else:
        return redirect("/NhanVien")


@app.route("/DangXuat", methods=["GET"])
def dang_xuat():
    if current_user.is_authenticated:
        logout_user()
    return redirect("/")


@app.route("/XemGioHang", methods=['GET'])
def xem_gio_hang():
    if current_user.is_authenticated and current_user.user_role == UserRole.KHACH_HANG:
        ds_don = None
        dict_tuyen_bay = None
        if 'gio_hang' in session:
            ds_don = dao.lay_ds_don(session['gio_hang'], current_user)
            dict_tuyen_bay = dao.lay_dict_tuyen_bay_theo_chuyen_bay()
        print(dict_tuyen_bay)
        return render_template("KhachHang/XemGioHang.html", ds_don=ds_don, dict_tuyen_bay=dict_tuyen_bay)
    else:
        return redirect("/DangNhap")


@app.route("/ThanhToan", methods=['POST'])
def thanh_toan():
    if current_user.is_authenticated and current_user.user_role == UserRole.KHACH_HANG:
        tong_tien = utils.lay_thong_tin(session['gio_hang'])["tong_tien"]
        thong_tin = "mua_ve_id_ghe_"
        for don_hang in session['gio_hang'].values():
            thong_tin += don_hang['id_ghe'] + "_"
        thong_tin = thong_tin[:-1]
        return redirect(vnpay.lay_url(tong_tien=tong_tien, thong_tin=thong_tin))
    else:
        return redirect("/DangNhap")


@app.route("/VNP", methods=['GET'])
def vnp_thanh_toan():
    ket_qua_thanh_toan = request.args.get("vnp_ResponseCode")
    thong_tin = request.args.get("vnp_OrderInfo")
    check = False
    if ket_qua_thanh_toan == "00":
        check = True
        if thong_tin.__contains__("mua_ve"):
            ds_don = dict(session['gio_hang'])
            for don in ds_don.values():
                dao.tao_ve_moi(id_chuyen_bay=int(don["id_chuyen_bay"]), id_ghe=int(don["id_ghe"]),
                               id_nguoi_dung=current_user.id_nguoi_dung, id_nhan_vien=None, hinh_thuc_thanh_toan=True)
            session['gio_hang'] = {}
        elif thong_tin.__contains__("cap_nhat"):
            id_ve, id_ghe, id_chuyen_bay = thong_tin.split("|")
            id_ve = id_ve[id_ve.find("=") + 2:len(id_ve)]
            id_ghe = id_ghe[id_ghe.find("=") + 2:len(id_ghe)]
            id_chuyen_bay = id_chuyen_bay[id_chuyen_bay.find("=") + 2:len(id_chuyen_bay)]
            dao.cap_nhat_ve(id_ve=id_ve, id_ghe=id_ghe, id_chuyen_bay=id_chuyen_bay, hinh_thuc_thanh_toan=True)
        else:
            id_chuyen_bay, id_ghe, id_nguoi_dung, id_nhan_vien = thong_tin.split("|")
            id_chuyen_bay = id_chuyen_bay[id_chuyen_bay.find("=") + 2:len(id_chuyen_bay)]
            id_ghe = id_ghe[id_ghe.find("=") + 2:len(id_ghe)]
            id_nguoi_dung = id_nguoi_dung[id_nguoi_dung.find("=") + 2:len(id_nguoi_dung)]
            id_nhan_vien = id_nhan_vien[id_nhan_vien.find("=") + 2:len(id_nhan_vien)]
            dao.tao_ve_moi(id_chuyen_bay=id_chuyen_bay, id_ghe=id_ghe, id_nguoi_dung=id_nguoi_dung,
                           id_nhan_vien=id_nhan_vien, hinh_thuc_thanh_toan=True)

    return render_template("ManHinhKetQuaThanhToan.html", check=check)


@app.route("/DatVe", methods=['GET'])
def dat_ve():
    if current_user.is_authenticated and current_user.user_role == UserRole.KHACH_HANG:
        id_chuyen_bay = request.args.get("id_chuyen_bay")
        chuyen_bay = None
        ds_bang_ghe = None
        dict_ve = None
        if id_chuyen_bay:
            chuyen_bay = dao.tra_cuu_chuyen_bay(id_chuyen_bay=id_chuyen_bay)[0]
            ds_bang_ghe, dict_ve = utils.lay_ds_ghe(id_chuyen_bay=id_chuyen_bay)
        link = "/DatVe?"
        return render_template('KhachHang/DatVe.html', link=link, chuyen_bay=chuyen_bay, ds_bang_ghe=ds_bang_ghe,
                               dict_ve=dict_ve)
    else:
        return redirect("/DangNhap")


@app.route("/XemThongTinNguoiDung", methods=['GET', 'POST'])
def xem_thong_tin_nguoi_dung():
    if current_user.is_authenticated and current_user.user_role == UserRole.KHACH_HANG:
        sl_so_dien_thoai = request.args.get("sl_so_dien_thoai")
        if sl_so_dien_thoai and int(sl_so_dien_thoai) <= 3 and int(sl_so_dien_thoai) >= 1:
            mes = None
            sl_so_dien_thoai = int(sl_so_dien_thoai)
            ds_so_dien_thoai = dao.lay_ds_so_dien_thoai_theo_id_nguoi_dung(current_user.id_nguoi_dung)
            print(current_user.gmail)
            if request.method == 'POST':
                ten_nguoi_dung = request.form.get("ten_nguoi_dung")
                CCCD = request.form.get("CCCD")
                mat_khau = request.form.get("mat_khau").strip()
                xac_nhan = request.form.get("xac_nhan").strip()
                anh_dai_dien = request.files.get("anh_dai_dien")
                gmail = request.form.get("gmail")
                if mat_khau == xac_nhan:
                    if dao.sua_nguoi_dung(current_user.id_nguoi_dung
                                        ,ten_nguoi_dung=ten_nguoi_dung
                                        ,CCCD=CCCD
                                        ,mat_khau=mat_khau
                                        ,tai_khoan=None
                                        ,hoat_dong=True
                                        ,gmail=gmail
                                        ,anh_dai_dien=anh_dai_dien):
                        kiem_tra = True
                        for so_dem in range(sl_so_dien_thoai):
                            if len(request.form.get("so_dien_thoai_"+str(so_dem)))!=10:
                                kiem_tra=False
                                break
                        if kiem_tra:
                            ds_so_dien_thoai_da_co = dao.lay_ds_so_dien_thoai(id_nguoi_dung=current_user.id_nguoi_dung)
                            dao.xoa_so_dien_thoai(id_nguoi_dung=current_user.id_nguoi_dung)
                            for so_dem in range(sl_so_dien_thoai):
                                kiem_tra = dao.tao_so_dien_thoai(id_nguoi_dung=current_user.id_nguoi_dung,so_dien_thoai=request.form.get("so_dien_thoai_"+str(so_dem)))
                                if kiem_tra:        
                                    ds_so_dien_thoai = dao.lay_ds_so_dien_thoai_theo_id_nguoi_dung(current_user.id_nguoi_dung)
                                    mes = "sửa thành công"
                                else:
                                    if so_dem == 0:
                                        dao.them_danh_sach_so_dien_thoai(ds_so_dien_thoai=ds_so_dien_thoai_da_co)
                                    mes = "số điện thoại đã được dùng"
                                    break
                        else:
                            mes = "số điện thoại không hợp lệ"
                else:
                    mes = "lỗi mật khẩu và xác nhận không trùng khớp"
            return render_template("KhachHang/ThongTinNguoiDung/XemThongTinNguoiDung.html", mes=mes,ds_so_dien_thoai=ds_so_dien_thoai,sl_so_dien_thoai=sl_so_dien_thoai)
        else:
            return redirect("/XemThongTinNguoiDung?sl_so_dien_thoai="+str(dao.lay_so_luong_so_dien_thoai_theo_id_nguoi_dung(id_nguoi_dung=current_user.id_nguoi_dung)))
    else:
        return redirect("/DangNhap")


@app.route("/XemThongTinNguoiDung/XemDSVe", methods=['GET'])
def xem_ds_ve():
    if current_user.is_authenticated and current_user.user_role == UserRole.KHACH_HANG:
        ds_ve = dao.tra_cuu_ve(id_nguoi_dung=current_user.id_nguoi_dung)
        return render_template("KhachHang/ThongTinNguoiDung/XemDSVe.html", ds_ve=ds_ve)
    else:
        return redirect("/DangNhap")


@app.route("/XemThongTinNguoiDung/XemLichSu", methods=['GET'])
def xem_lich_su():
    if current_user.is_authenticated and current_user.user_role == UserRole.KHACH_HANG:
        ds_ve = dao.tra_cuu_ve(id_nguoi_dung=current_user.id_nguoi_dung, lich_su=True)
        return render_template("KhachHang/ThongTinNguoiDung/XemLichSu.html", ds_ve=ds_ve)
    else:
        return redirect("/DangNhap")


@app.route("/XemThongTinNguoiDung/HuyVe", methods=['GET', 'POST'])
def huy_ve():
    if current_user.is_authenticated and current_user.user_role == UserRole.KHACH_HANG:
        mes = None
        id_ve = request.args.get("id_ve")
        ve = dao.tra_cuu_ve(id_ve=id_ve)[0]
        bang_ngan_hang = dao.lay_bang_ngan_hang()
        if request.method == "POST":
            so_tai_khoan = request.form.get("so_tai_khoan")
            id_ngan_hang = request.form.get("id_ngan_hang")
            if id_ngan_hang:
                if len(so_tai_khoan) == 16:
                    dao.xoa_ve_theo_id(id_ve)
                    dao.tao_don_huy(id_chuyen_bay=ve.Ve.id_chuyen_bay,
                                    id_ghe=ve.Ghe.id_ghe,
                                    id_khach_hang=current_user.id_nguoi_dung,
                                    id_ngan_hang=id_ngan_hang,
                                    id_nhan_vien=None,
                                    so_tai_khoan=so_tai_khoan)
                    return redirect("/XemThongTinNguoiDung/XemDSVe")
                else:
                    mes = "số tài khoản không đúng định dạng (phải có 16 số)"
            else:
                mes = "chưa chọn ngân hàng"
        return render_template("KhachHang/ThongTinNguoiDung/HuyVe.html", bang=bang_ngan_hang, mes=mes, ve=ve)
    else:
        return redirect("/DangNhap")


@app.route("/XemThongTinNguoiDung/XemDSDonHuy", methods=['GET', 'POST'])
def xem_ds_don_huy():
    if current_user.is_authenticated and current_user.user_role == UserRole.KHACH_HANG:
        ds_don_huy = dao.lay_ds_don_huy()
        return render_template("KhachHang/ThongTinNguoiDung/XemDSDonHuy.html", ds_don_huy=ds_don_huy)
    else:
        return redirect("/DangNhap")


@app.route("/XemThongTinNguoiDung/CapNhatVe", methods=['GET', 'POST'])
def cap_nhat_ve_khach_hang():
    if current_user.is_authenticated and current_user.user_role == UserRole.KHACH_HANG:

        err = ""
        id_chuyen_bay = request.args.get("id_chuyen_bay")
        id_ve = request.args.get("id_ve")

        chuyen_bay = dao.tra_cuu_chuyen_bay(id_chuyen_bay=id_chuyen_bay)[0]
        ds_bang_ghe, dict_ve = utils.lay_ds_ghe(id_chuyen_bay=id_chuyen_bay)

        link = "/XemThongTinNguoiDung/CapNhatVe?id_ve=" + id_ve + "&id_chuyen_bay=" + id_chuyen_bay
        link_tra_cuu_chuyen_bay = "/XemThongTinNguoiDung/CapNhatVe?id_ve=" + id_ve + ";"

        if request.method == "POST":
            id_ghe = request.form.get("id_ghe")
            if id_ghe == None:
                err = "yêu cầu chọn ghế"

            if id_chuyen_bay and id_ghe:
                thong_tin = "cap_nhat_ve_id_ve_=_" + id_ve + "|id_ghe_=_" + id_ghe + "|id_chuyen_bay_=_" + id_chuyen_bay

                gia_tien_ve_moi = dao.lay_quy_dinh_hang_ve(id_ghe=id_ghe).QuyDinhHangVe.don_gia
                ve = dao.tra_cuu_ve(id_ve=id_ve)[0]
                gia_tien_ve_cu = dao.lay_quy_dinh_hang_ve(id_ghe=ve.Ghe.id_ghe).QuyDinhHangVe.don_gia
                tong_tien = (gia_tien_ve_moi - gia_tien_ve_cu) if (gia_tien_ve_moi - gia_tien_ve_cu) > 0 else 0
                tong_tien += 200000

                return redirect(vnpay.lay_url(thong_tin=thong_tin, tong_tien=tong_tien))

        return render_template("KhachHang/ThongTinNguoiDung/CapNhatVe.html"
                               , link_tra_cuu_chuyen_bay=link_tra_cuu_chuyen_bay
                               , err=err
                               , nguoi_dung=current_user
                               , link=link
                               , chuyen_bay=chuyen_bay
                               , ds_bang_ghe=ds_bang_ghe
                               , dict_ve=dict_ve)
    else:
        return redirect("/DangNhap")


# admin
@app.route("/admin-login", methods=["POST"])
def dang_nhap_quan_tri():
    if request.method == 'POST':
        tai_khoan = request.form.get("tai_khoan").strip()
        mat_khau = request.form.get("mat_khau").strip()
        quan_tri = dao.kiem_tra_tai_khoan(tai_khoan=tai_khoan, mat_khau=mat_khau, user_role=UserRole.QUAN_TRI)
        if quan_tri:
            login_user(quan_tri)
        return redirect("/admin")


# nhan_vien
@app.route("/NhanVien", methods=['GET', 'POST'])
def dang_nhap_nhan_vien():
    if not (current_user.is_authenticated and current_user.user_role == UserRole.KHACH_HANG):
        session['nguoi_dung'] = False
        err = None
        if request.method == "POST":
            tai_khoan = request.form.get("tai_khoan").strip()
            mat_khau = request.form.get("mat_khau").strip()
            nhan_vien = dao.kiem_tra_tai_khoan(tai_khoan=tai_khoan, mat_khau=mat_khau, user_role=UserRole.NHAN_VIEN)
            if nhan_vien:
                login_user(nhan_vien)
            else:
                err = "sai mật khẩu hoặc tài khoản"
        return render_template("NhanVien/DangNhap.html", err=err)
    else:
        return redirect("/")


@app.route("/NhanVien/QuanLyKhachHang", methods=['GET'])
def quan_ly_khach_hang():
    if current_user.is_authenticated and current_user.user_role == UserRole.NHAN_VIEN:
        CCCD = request.args.get("CCCD")
        gmail = request.args.get("gmail")
        ds_khach_hang = dao.lay_ds_nguoi_dung(gmail=gmail, CCCD=CCCD, user_role=UserRole.KHACH_HANG)
        return render_template("NhanVien/QuanLyKhachHang/QuanLyKhachHang.html", ds_khach_hang=ds_khach_hang)
    else:
        return redirect("/NhanVien")


@app.route("/NhanVien/QuanLyKhachHang/CapNhatKhachHang", methods=['GET', 'POST'])
def cap_nhat_khach_hang():
    if current_user.is_authenticated and current_user.user_role == UserRole.NHAN_VIEN:
        sl_so_dien_thoai = request.args.get("sl_so_dien_thoai")
        id_khach_hang = request.args.get('id_khach_hang')
        if sl_so_dien_thoai and int(sl_so_dien_thoai) <= 3 and int(sl_so_dien_thoai) >= 1:
            sl_so_dien_thoai = int(sl_so_dien_thoai)
            err=None
            khach_hang = dao.lay_nguoi_dung_theo_id(id_nguoi_dung=id_khach_hang)
            ds_so_dien_thoai = dao.lay_ds_so_dien_thoai_theo_id_nguoi_dung(id_nguoi_dung=id_khach_hang)
            if request.method == 'POST':
                ten_khach_hang = request.form.get("ten_nguoi_dung")
                gmail = request.form.get("gmail")
                CCCD = request.form.get("CCCD")
                tai_khoan = request.form.get("tai_khoan").strip()
                hoat_dong = request.form.get("hoat_dong")
                hoat_dong = True if hoat_dong else False
                kiem_tra = True
                for so_dem in range(sl_so_dien_thoai):
                    if len(request.form.get("so_dien_thoai_"+str(so_dem)))!=10:
                        kiem_tra=False
                        break
                if kiem_tra:
                    nguoi_dung = dao.sua_nguoi_dung(id_nguoi_dung=id_khach_hang
                                                    ,ten_nguoi_dung=ten_khach_hang
                                                    , gmail=gmail
                                                    , CCCD=CCCD
                                                    , mat_khau=None
                                                    , hoat_dong=hoat_dong
                                                    , tai_khoan=tai_khoan
                                                    , anh_dai_dien=None)
                    
                    if nguoi_dung:
                        ds_so_dien_thoai_da_co = dao.lay_ds_so_dien_thoai(id_nguoi_dung=nguoi_dung.id_nguoi_dung)
                        dao.xoa_so_dien_thoai(id_nguoi_dung=nguoi_dung.id_nguoi_dung)
                        for so_dem in range(sl_so_dien_thoai):
                            kiem_tra = dao.tao_so_dien_thoai(id_nguoi_dung=nguoi_dung.id_nguoi_dung,so_dien_thoai=request.form.get("so_dien_thoai_"+str(so_dem)))
                            if kiem_tra:        
                                ds_so_dien_thoai = dao.lay_ds_so_dien_thoai_theo_id_nguoi_dung(nguoi_dung.id_nguoi_dung)
                                err = "sửa thành công"
                            else:
                                if so_dem == 0:
                                    dao.them_danh_sach_so_dien_thoai(ds_so_dien_thoai=ds_so_dien_thoai_da_co)
                                err = "số điện thoại đã được dùng"
                                break
                    else:
                        err="thông tin đã được sử dụng"
                else:
                    err = "số điện thoại không hợp lệ"
            return render_template("/NhanVien/QuanLyKhachHang/CapNhatKhachHang.html",sl_so_dien_thoai=sl_so_dien_thoai ,khach_hang=khach_hang,ds_so_dien_thoai=ds_so_dien_thoai,err=err)
        else:
            return redirect("/NhanVien/QuanLyKhachHang/CapNhatKhachHang?id_khach_hang="+str(id_khach_hang)+"&sl_so_dien_thoai="+str(dao.lay_so_luong_so_dien_thoai_theo_id_nguoi_dung(id_nguoi_dung=id_khach_hang)))
    else:
        return redirect("/NhanVien")


@app.route("/NhanVien/QuanLyKhachHang/TaoKhachHang", methods=['GET', 'POST'])
def tao_khach_hang():
    if current_user.is_authenticated and current_user.user_role == UserRole.NHAN_VIEN:
        sl_so_dien_thoai = request.args.get("sl_so_dien_thoai")
        if sl_so_dien_thoai and int(sl_so_dien_thoai) <= 3 and int(sl_so_dien_thoai) >= 1:
            sl_so_dien_thoai = int(sl_so_dien_thoai)
            err = None
            if request.method == "POST":
                ten_nguoi_dung = request.form.get("ten_nguoi_dung")
                gmail = request.form.get("gmail")
                CCCD = request.form.get("CCCD")
                tai_khoan = request.form.get("tai_khoan").strip()
                kiem_tra = True
                for so_dem in range(sl_so_dien_thoai):
                    if len(request.form.get("so_dien_thoai_"+str(so_dem)))!=10:
                        kiem_tra=False
                        break
                if kiem_tra:
                    nguoi_dung = dao.tao_nguoi_dung_moi(ten_nguoi_dung=ten_nguoi_dung, gmail=gmail, CCCD=CCCD,
                                mat_khau=None, hoat_dong=None, tai_khoan=tai_khoan, anh_dai_dien=None)
                    if nguoi_dung:
                        dao.xoa_so_dien_thoai(id_nguoi_dung=nguoi_dung.id_nguoi_dung)
                        for so_dem in range(sl_so_dien_thoai):
                            kiem_tra = dao.tao_so_dien_thoai(id_nguoi_dung=nguoi_dung.id_nguoi_dung,so_dien_thoai=request.form.get("so_dien_thoai_"+str(so_dem)))
                            if kiem_tra:
                                return redirect("/NhanVien/QuanLyKhachHang")
                            else:
                                err = "số điện thoại này đã được dùng"
                                break
                    else:
                        err = "thông tin này đã được dùng"
                else:
                    err = "số điện thoại không hợp lệ"
            return render_template("/NhanVien/QuanLyKhachHang/TaoKhachHang.html", err=err,sl_so_dien_thoai=sl_so_dien_thoai)
        else:
            return redirect("/NhanVien/QuanLyKhachHang/TaoKhachHang?sl_so_dien_thoai="+str(1))
    else:
        return redirect("/NhanVien")


@app.route("/NhanVien/QuanLyKhachHang/XoaKhachHang", methods=['GET'])
def xoa_khach_hang():
    if current_user.is_authenticated and current_user.user_role == UserRole.NHAN_VIEN:
        id_khach_hang = request.args.get("id_khach_hang")
        dao.xoa_khach_hang_theo_id(id_khach_hang=id_khach_hang)
        dao.xoa_nguoi_dung_theo_id(id_nguoi_dung=id_khach_hang)
        return redirect("/NhanVien/QuanLyKhachHang")
    else:
        return redirect("/NhanVien")


@app.route("/NhanVien/QuanLyLichChuyenBay", methods=['GET'])
def quan_ly_lich_chuyen_bay():
    if current_user.is_authenticated and current_user.user_role == UserRole.NHAN_VIEN:
        err = request.args.get("err")
        ngay_gio = request.args.get("ngay_gio")
        ten_chuyen_bay = request.args.get("ten_chuyen_bay")
        ds_lich_chuyen_bay = dao.tra_cuu_lich_chuyen_bay(ngay_gio=ngay_gio, ten_chuyen_bay=ten_chuyen_bay)
        return render_template("NhanVien/QuanLyLichChuyenBay/QuanLyLichChuyenBay.html", err=err,
                               ds_lich_chuyen_bay=ds_lich_chuyen_bay)
    else:
        return redirect("/NhanVien")


@app.route("/NhanVien/QuanLyLichChuyenBay/LapLichChuyenBay", methods=['GET', 'POST'])
def lap_lich_chuyen_bay():
    if current_user.is_authenticated and current_user.user_role == UserRole.NHAN_VIEN:
        id_chuyen_bay = request.args.get("id_chuyen_bay")
        so_luong_san_bay = request.args.get("so_luong_san_bay")
        so_luong_san_bay = int(so_luong_san_bay) if so_luong_san_bay else 0
        err = None
        link = ""
        link_tra_cuu_chuyen_bay = "/NhanVien/QuanLyLichChuyenBay/LapLichChuyenBay?"
        ds_san_bay = []
        chuyen_bay = None
        if id_chuyen_bay:
            chuyen_bay = dao.tra_cuu_chuyen_bay(id_chuyen_bay=id_chuyen_bay)[0]
            if so_luong_san_bay > chuyen_bay.QuyDinh.SL_san_bay_toi_da:
                err = "quá số lượng quy định"
                so_luong_san_bay -= 1

            link += ("id_chuyen_bay=" + str(id_chuyen_bay) + "&")

            for so_dem in range(so_luong_san_bay):
                id_san_bay = request.args.get("id_san_bay_" + str(so_dem))
                ds_san_bay.append(dao.lay_san_bay_theo_id(id_san_bay))
                if id_san_bay:
                    link += ("id_san_bay_" + str(so_dem) + '=' + id_san_bay + "&")

            link += "so_luong_san_bay=" + str(so_luong_san_bay)
        if request.method == "POST":
            id_chuyen_bay = request.form.get("id_chuyen_bay")
            ngay_gio = request.form.get("ngay_gio")
            thoi_gian_bay = request.form.get("thoi_gian_bay")

            ds_id_san_bay = []
            ds_thoi_gian_dung = []
            ds_ghi_chu = []
            for so_dem in range(so_luong_san_bay):
                ds_id_san_bay.append(request.form.get("id_san_bay_" + str(so_dem)))
                ds_thoi_gian_dung.append(request.form.get("thoi_gian_dung_" + str(so_dem)))
                ds_ghi_chu.append(request.form.get("ghi_chu_" + str(so_dem)))

            err = utils.tao_hoac_sua_lich_chuyen_bay(ngay_gio=ngay_gio, thoi_gian_bay=thoi_gian_bay,
                                                     ds_thoi_gian_dung=ds_thoi_gian_dung, quy_dinh=chuyen_bay.QuyDinh,
                                                     id_chuyen_bay=id_chuyen_bay, so_luong_san_bay=so_luong_san_bay,
                                                     ds_id_san_bay=ds_id_san_bay, ds_ghi_chu=ds_ghi_chu,
                                                     tao_hoac_sua=dao.tao_lich_chuyen_bay)
            if not (err):
                return redirect("/NhanVien/QuanLyLichChuyenBay")

        return render_template("NhanVien/QuanLyLichChuyenBay/LapLichChuyenBay.html",
                               link_tra_cuu_chuyen_bay=link_tra_cuu_chuyen_bay, err=err, ds_san_bay=ds_san_bay,
                               chuyen_bay=chuyen_bay, so_luong_san_bay=so_luong_san_bay, link=link)
    else:
        return redirect("/NhanVien")


@app.route("/NhanVien/QuanLyLichChuyenBay/TraCuuSanBay", methods=['GET'])
def tra_cuu_san_bay():
    if current_user.is_authenticated and current_user.user_role == UserRole.NHAN_VIEN:
        ten_san_bay = request.args.get("ten_san_bay")
        id_chuyen_bay = request.args.get("id_chuyen_bay")
        id_lich_chuyen_bay = request.args.get("id_lich_chuyen_bay")
        so_luong_san_bay = int(request.args.get("so_luong_san_bay"))
        if id_chuyen_bay:
            link = ("/LapLichChuyenBay?id_chuyen_bay=" + str(id_chuyen_bay))
        else:
            link = ("/CapNhatLichChuyenBay?id_lich_chuyen_bay=" + str(id_lich_chuyen_bay))
        ds_id_san_bay_da_co = []

        for so_dem in range(so_luong_san_bay):
            id_san_bay = request.args.get("id_san_bay_" + str(so_dem))
            ds_id_san_bay_da_co.append(id_san_bay)
            link += ("&id_san_bay_" + str(so_dem) + '=' + id_san_bay)
        if id_chuyen_bay:
            chuyen_bay = dao.lay_chuyen_bay_theo_id(id_chuyen_bay=id_chuyen_bay)
        else:
            chuyen_bay = dao.lay_chuyen_bay_theo_id(id_chuyen_bay=id_lich_chuyen_bay)
        tuyen_bay = dao.lay_tuyen_bay_theo_id(chuyen_bay.id_tuyen_bay)
        ds_sanbay_tuyenbay = dao.lay_ds_san_bay_tuyen_bay_theo_id_tuyen_bay(tuyen_bay.id_tuyen_bay)
        for sanbay_tuyenbay in ds_sanbay_tuyenbay:
            ds_id_san_bay_da_co.append(sanbay_tuyenbay.id_san_bay)
        ds_san_bay = dao.lay_ds_san_bay_con_lai(ds_id_san_bay=ds_id_san_bay_da_co, ten_san_bay=ten_san_bay)
        return render_template("NhanVien/QuanLyLichChuyenBay/TraCuuSanBay.html",
                               link=link,
                               ds_san_bay=ds_san_bay,
                               id_chuyen_bay=id_chuyen_bay,
                               id_lich_chuyen_bay=id_lich_chuyen_bay,
                               ds_id_san_bay_da_co=ds_id_san_bay_da_co,
                               so_luong_san_bay=so_luong_san_bay)
    else:
        return redirect("/NhanVien")


@app.route("/NhanVien/QuanLyLichChuyenBay/XoaSanBay", methods=['GET'])
def xoa_san_bay():
    if current_user.is_authenticated and current_user.user_role == UserRole.NHAN_VIEN:
        id_chuyen_bay = request.args.get("id_chuyen_bay")
        id_lich_chuyen_bay = request.args.get("id_lich_chuyen_bay")
        so_luong_san_bay = int(request.args.get("so_luong_san_bay"))
        if id_chuyen_bay:
            link = ("LapLichChuyenBay?id_chuyen_bay=" + str(id_chuyen_bay))
        else:
            link = ("CapNhatLichChuyenBay?id_lich_chuyen_bay=" + str(id_lich_chuyen_bay))
        so_dem_san_bay = int(request.args.get("so_dem_san_bay"))
        ds_id_san_bay_da_co = []

        for so_dem in range(so_luong_san_bay):
            id_san_bay = request.args.get("id_san_bay_" + str(so_dem))
            ds_id_san_bay_da_co.append(id_san_bay)
            if id_san_bay:
                if so_dem < so_dem_san_bay:
                    link += ("&id_san_bay_" + str(so_dem) + '=' + id_san_bay)
                elif so_dem > so_dem_san_bay:
                    link += ("&id_san_bay_" + str(so_dem - 1) + '=' + id_san_bay)

        so_luong_san_bay -= 1
        return redirect("/NhanVien/QuanLyLichChuyenBay/" + link + "&so_luong_san_bay=" + str(so_luong_san_bay))
    else:
        return redirect("/NhanVien")


@app.route("/NhanVien/QuanLyLichChuyenBay/XoaLichChuyenBay", methods=['GET'])
def xoa_lich_chuyen_bay():
    if current_user.is_authenticated and current_user.user_role == UserRole.NHAN_VIEN:
        id_lich_chuyen_bay = request.args.get("id_lich_chuyen_bay")
        err = None
        chuyen_bay = dao.lay_chuyen_bay_theo_id(id_lich_chuyen_bay)
        if len(chuyen_bay.ds_ve) == 0:
            dao.xoa_san_bay_trung_gian_theo_id_lich(id_lich_chuyen_bay=id_lich_chuyen_bay)
            dao.xoa_lich_chuyen_bay(id_lich_chuyen_bay=id_lich_chuyen_bay)
        else:
            err = "True"
        link = "/NhanVien/QuanLyLichChuyenBay"
        link += ("?err=" + err) if err else ""
        return redirect(link)
    else:
        return redirect("/NhanVien")


@app.route("/NhanVien/QuanLyLichChuyenBay/CapNhatLichChuyenBay", methods=['GET', 'POST'])
def cap_nhat_lich_chuyen_bay():
    if current_user.is_authenticated and current_user.user_role == UserRole.NHAN_VIEN:
        id_lich_chuyen_bay = request.args.get("id_lich_chuyen_bay")
        err = None
        chuyen_bay = dao.lay_chuyen_bay_theo_id(id_lich_chuyen_bay)
        if len(chuyen_bay.ds_ve) == 0:
            id_lich_chuyen_bay = int(request.args.get("id_lich_chuyen_bay"))
            so_luong_san_bay = request.args.get("so_luong_san_bay")
            link = "id_lich_chuyen_bay=" + str(id_lich_chuyen_bay)
            if not (so_luong_san_bay):
                ds_san_bay_trung_gian = dao.lay_ds_san_bay_trung_gian_theo_id_lich(
                    id_lich_chuyen_bay=id_lich_chuyen_bay)
                so_luong_san_bay = len(ds_san_bay_trung_gian)
                for so_dem_san_bay in range(so_luong_san_bay):
                    link += ("&id_san_bay_" + str(so_dem_san_bay) + "=" + str(
                        ds_san_bay_trung_gian[so_dem_san_bay].id_san_bay))
                link += str("&so_luong_san_bay=" + str(so_luong_san_bay))
                return redirect("/NhanVien/QuanLyLichChuyenBay/CapNhatLichChuyenBay?" + link)
            else:
                so_luong_san_bay = int(so_luong_san_bay)
                chuyen_bay = dao.tra_cuu_chuyen_bay(id_chuyen_bay=id_lich_chuyen_bay)[0]

                if so_luong_san_bay > chuyen_bay.QuyDinh.SL_san_bay_toi_da:
                    err = "quá số lượng quy định"
                    so_luong_san_bay -= 1

                ds_san_bay = []
                for so_dem in range(so_luong_san_bay):
                    id_san_bay = request.args.get("id_san_bay_" + str(so_dem))
                    ds_san_bay.append(dao.lay_san_bay_theo_id(id_san_bay))
                    link += ("&id_san_bay_" + str(so_dem) + "=" + request.args.get("id_san_bay_" + str(so_dem)))
                link += str("&so_luong_san_bay=" + str(so_luong_san_bay))

                dict_san_bay_trung_gian = dao.lay_dict_san_bay_trung_gian_theo_san_bay(
                    id_lich_chuyen_bay=id_lich_chuyen_bay)

            if request.method == "POST":
                ngay_gio = request.form.get("ngay_gio")
                thoi_gian_bay = request.form.get("thoi_gian_bay")
                id_lich_chuyen_bay = request.args.get("id_lich_chuyen_bay")
                quy_dinh = dao.lay_quy_dinh_theo_id(chuyen_bay.QuyDinh.id_quy_dinh)

                ds_thoi_gian_dung = []
                ds_id_san_bay = []
                ds_ghi_chu = []
                for so_dem in range(so_luong_san_bay):
                    ds_id_san_bay.append(request.form.get("id_san_bay_" + str(so_dem)))
                    ds_thoi_gian_dung.append(request.form.get("thoi_gian_dung_" + str(so_dem)))
                    ds_ghi_chu.append(request.form.get("ghi_chu_" + str(so_dem)))

                ds_san_bay_trung_gian = dao.lay_ds_san_bay_trung_gian_theo_id_lich(
                    id_lich_chuyen_bay=id_lich_chuyen_bay)
                dao.xoa_san_bay_trung_gian_theo_id_lich(id_lich_chuyen_bay=id_lich_chuyen_bay)

                err = utils.tao_hoac_sua_lich_chuyen_bay(ngay_gio=ngay_gio, thoi_gian_bay=thoi_gian_bay,
                                                         ds_thoi_gian_dung=ds_thoi_gian_dung, quy_dinh=quy_dinh,
                                                         id_chuyen_bay=id_lich_chuyen_bay,
                                                         so_luong_san_bay=so_luong_san_bay, ds_id_san_bay=ds_id_san_bay,
                                                         ds_ghi_chu=ds_ghi_chu, tao_hoac_sua=dao.sua_lich_chuyen_bay)
                if not (err):
                    return redirect("/NhanVien/QuanLyLichChuyenBay")
                else:
                    dao.them_san_bay_trung_gian_theo_ds(ds_san_bay_trung_gian=ds_san_bay_trung_gian)
            return render_template("NhanVien/QuanLyLichChuyenBay/CapNhatLichChuyenBay.html",
                                   err=err,
                                   link=link,
                                   chuyen_bay=chuyen_bay,
                                   ds_san_bay=ds_san_bay,
                                   dict_san_bay_trung_gian=dict_san_bay_trung_gian)
        else:
            link = "/NhanVien/QuanLyLichChuyenBay?err=True"
            return redirect(link)
    else:
        return redirect("/NhanVien")


@app.route("/NhanVien/XemDSDonHuy", methods=['GET', 'POST'])
def xem_ds_don_huy_khach_hang():
    if current_user.is_authenticated and current_user.user_role == UserRole.NHAN_VIEN:
        ds_don_huy = dao.lay_ds_don_huy()
        return render_template("NhanVien/XemDSDonHuy.html", ds_don_huy=ds_don_huy)
    else:
        return redirect("/NhanVien")


@app.route("/NhanVien/CapNhatDonHuy", methods=['GET'])
def cap_nhat_don_huy():
    if current_user.is_authenticated and current_user.user_role == UserRole.NHAN_VIEN:
        id_don_huy = request.args.get("id_don_huy")
        dao.sua_don_huy(id_don_huy=id_don_huy, id_nhan_vien=current_user.id_nguoi_dung)
        return redirect("/NhanVien/XemDSDonHuy")
    else:
        return redirect("/NhanVien")


@app.route("/NhanVien/QuanLyVe", methods=['GET', 'POST'])
def quan_ly_ve():
    if current_user.is_authenticated and current_user.user_role == UserRole.NHAN_VIEN:
        id_tuyen_bay = None if request.args.get("id_tuyen_bay") == "None" else request.args.get("id_tuyen_bay")
        ten_nguoi_dung = request.args.get("ten_nguoi_dung") if request.args.get("ten_nguoi_dung") else ""
        ds_ve = dao.tra_cuu_ve(id_tuyen_bay=id_tuyen_bay, ten_nguoi_dung=ten_nguoi_dung)
        ds_tuyen_bay = dao.lay_ds_tuyen_bay(trang=None, ten_tuyen_bay=None)
        return render_template("NhanVien/QuanLyVe/QuanLyVe.html", ds_ve=ds_ve, ds_tuyen_bay=ds_tuyen_bay)
    else:
        return redirect("/NhanVien")


@app.route("/NhanVien/QuanLyVe/BanVe", methods=['GET', 'POST'])
def ban_ve():
    if current_user.is_authenticated and current_user.user_role == UserRole.NHAN_VIEN:
        err = None
        id_chuyen_bay = request.args.get("id_chuyen_bay")
        id_nguoi_dung = request.args.get("id_nguoi_dung")

        link_tra_cuu_chuyen_bay = "/NhanVien/QuanLyVe/BanVe?"
        link_tra_cuu_nguoi_dung = link_tra_cuu_chuyen_bay
        link = link_tra_cuu_chuyen_bay

        chuyen_bay = None
        ds_bang_ghe = None
        dict_ve = None

        if id_chuyen_bay:
            link_tra_cuu_nguoi_dung += "id_chuyen_bay=" + id_chuyen_bay + ";"
            chuyen_bay = dao.tra_cuu_chuyen_bay(id_chuyen_bay=id_chuyen_bay)[0]

            ds_bang_ghe, dict_ve = utils.lay_ds_ghe(id_chuyen_bay=id_chuyen_bay)
            link += "id_chuyen_bay=" + id_chuyen_bay + "&"

        if id_nguoi_dung:
            link_tra_cuu_chuyen_bay += "id_nguoi_dung=" + id_nguoi_dung + ";"
            link += "id_nguoi_dung=" + id_nguoi_dung

        nguoi_dung = dao.lay_nguoi_dung_theo_id(id_nguoi_dung=id_nguoi_dung)

        if request.method == "POST":
            if id_chuyen_bay == None:
                err = "yêu cầu cung cấp chuyến bay"

            if id_nguoi_dung == None:
                err = "yêu cầu cung cấp khách hàng"

            id_ghe = request.form.get("id_ghe")
            if id_ghe == None:
                err = "yêu cầu chọn ghế"

            hinh_thuc_thanh_toan = request.form.get("hinh_thuc_thanh_toan")
            hinh_thuc_thanh_toan = True if hinh_thuc_thanh_toan else False

            if id_chuyen_bay and id_nguoi_dung and id_ghe:
                if not (hinh_thuc_thanh_toan):
                    dao.tao_ve_moi(id_nguoi_dung=int(id_nguoi_dung), id_chuyen_bay=int(id_chuyen_bay),
                                   id_ghe=int(id_ghe), id_nhan_vien=current_user.id_nguoi_dung,
                                   hinh_thuc_thanh_toan=False)
                    ds_bang_ghe, dict_ve = utils.lay_ds_ghe(id_chuyen_bay=id_chuyen_bay)
                else:

                    quy_dinh_hang_ve = dao.lay_quy_dinh_hang_ve(id_ghe=id_ghe)
                    gia_ban = quy_dinh_hang_ve.QuyDinhHangVe.gia_ban

                    thong_tin = "ban_ve_id_chuyen_bay_=_" + str(id_chuyen_bay) + "|id_ghe_=_" + str(
                        id_ghe) + "|id_nguoi_dung_=_" + str(id_nguoi_dung) + "|id_nhan_vien_=_" + str(
                        current_user.id_nguoi_dung)
                    return redirect(vnpay.lay_url(tong_tien=gia_ban, thong_tin=thong_tin))

        return render_template("NhanVien/QuanLyVe/BanVe.html"
                               , link=link
                               , err=err
                               , nguoi_dung=nguoi_dung
                               , link_tra_cuu_chuyen_bay=link_tra_cuu_chuyen_bay
                               , link_tra_cuu_nguoi_dung=link_tra_cuu_nguoi_dung
                               , chuyen_bay=chuyen_bay
                               , ds_bang_ghe=ds_bang_ghe
                               , dict_ve=dict_ve)
    else:
        return redirect("/NhanVien")


@app.route("/NhanVien/QuanLyVe/TraCuuKhachHang", methods=['GET'])
def tra_cuu_khach_hang():
    if current_user.is_authenticated and current_user.user_role == UserRole.NHAN_VIEN:
        link = request.args.get("link")
        link = link.replace(";", "&")
        gmail = request.args.get("gmail")
        CCCD = request.args.get("CCCD")
        ds_khach_hang = dao.lay_ds_nguoi_dung(gmail=gmail, CCCD=CCCD, user_role=UserRole.KHACH_HANG)
        return render_template("NhanVien/QuanLyVe/TraCuuKhachHang.html", ds_khach_hang=ds_khach_hang, link=link)
    else:
        return redirect("/NhanVien")


@app.route("/NhanVien/QuanLyVe/XoaVe", methods=['GET', 'POST'])
def xoa_ve():
    if current_user.is_authenticated and current_user.user_role == UserRole.NHAN_VIEN:
        mes = ""
        id_ve = request.args.get("id_ve")

        ve = dao.tra_cuu_ve(id_ve=id_ve)[0]
        bang_ngan_hang = dao.lay_bang_ngan_hang()

        if request.method == "POST":

            so_tai_khoan = request.form.get("so_tai_khoan")
            id_ngan_hang = request.form.get("id_ngan_hang")
            hinh_thuc_hoan_tra = True if request.form.get("hinh_thuc_hoan_tra") else False

            if hinh_thuc_hoan_tra:
                if id_ngan_hang:
                    if len(so_tai_khoan) == 16:
                        dao.xoa_ve_theo_id(id_ve)
                        dao.tao_don_huy(id_chuyen_bay=ve.ChuyenBay.id_chuyen_bay,
                                        id_ghe=ve.Ghe.id_ghe,
                                        id_khach_hang=ve.KhachHang.id_khach_hang,
                                        id_ngan_hang=id_ngan_hang,
                                        id_nhan_vien=current_user.id_nguoi_dung,
                                        so_tai_khoan=so_tai_khoan)
                        return redirect("/NhanVien/QuanLyVe")
                    else:
                        mes = "số tài khoản không đúng định dạng (phải có 16 số)"
                else:
                    mes = "chưa chọn ngân hàng"
            else:
                dao.xoa_ve_theo_id(id_ve)
                dao.tao_don_huy(id_chuyen_bay=ve.ChuyenBay.id_chuyen_bay,
                                id_ghe=ve.Ghe.id_ghe,
                                id_khach_hang=ve.KhachHang.id_khach_hang,
                                id_ngan_hang=None,
                                id_nhan_vien=current_user.id_nguoi_dung,
                                so_tai_khoan=None)
                return redirect("/NhanVien/QuanLyVe")
        return render_template("NhanVien/QuanLyVe/XoaVe.html", bang=bang_ngan_hang, ve=ve, mes=mes)
    else:
        return redirect("/DangNhap")


@app.route("/NhanVien/QuanLyVe/CapNhatVe", methods=['GET', 'POST'])
def cap_nhat_ve():
    if current_user.is_authenticated and current_user.user_role == UserRole.NHAN_VIEN:
        err = None
        id_chuyen_bay = request.args.get("id_chuyen_bay")
        id_ve = request.args.get("id_ve")
        id_nguoi_dung = request.args.get("id_nguoi_dung")

        link = "?id_ve=" + id_ve
        link_tra_cuu_chuyen_bay = "/NhanVien/QuanLyVe/CapNhatVe?id_ve=" + id_ve + ";"

        link += "&id_chuyen_bay=" + id_chuyen_bay
        ds_bang_ghe, dict_ve = utils.lay_ds_ghe(id_chuyen_bay=id_chuyen_bay)
        link += "&id_nguoi_dung=" + id_nguoi_dung
        link_tra_cuu_chuyen_bay += "id_nguoi_dung=" + id_nguoi_dung + ";"

        chuyen_bay = dao.tra_cuu_chuyen_bay(id_chuyen_bay=id_chuyen_bay)[0]
        nguoi_dung = dao.lay_nguoi_dung_theo_id(id_nguoi_dung=id_nguoi_dung)
        ve = dao.tra_cuu_ve(id_ve=id_ve)[0]

        if request.method == "POST":
            id_ghe = request.form.get("id_ghe")
            hinh_thuc_thanh_toan = request.form.get("hinh_thuc_thanh_toan")
            hinh_thuc_thanh_toan = True if hinh_thuc_thanh_toan else False

            if id_ghe == None:
                err = "yêu cầu chọn ghế"
            if id_chuyen_bay and id_nguoi_dung and id_ghe:
                if not (hinh_thuc_thanh_toan):
                    dao.cap_nhat_ve(id_ve=id_ve, id_chuyen_bay=id_chuyen_bay, id_ghe=id_ghe, hinh_thuc_thanh_toan=False)
                    ds_bang_ghe, dict_ve = utils.lay_ds_ghe(id_chuyen_bay=id_chuyen_bay)
                else:
                    thong_tin = "cap_nhat_ve_id_ve_=_" + id_ve + "|id_ghe_=_" + id_ghe + "|id_chuyen_bay_=_" + id_chuyen_bay

                    gia_tien_ve_moi = dao.lay_quy_dinh_hang_ve(id_ghe=id_ghe).QuyDinhHangVe.don_gia
                    ve = dao.tra_cuu_ve(id_ve=id_ve)[0]
                    gia_tien_ve_cu = dao.lay_quy_dinh_hang_ve(id_ghe=ve.Ghe.id_ghe).QuyDinhHangVe.don_gia
                    tong_tien = (gia_tien_ve_moi - gia_tien_ve_cu) if gia_tien_ve_moi - gia_tien_ve_cu > 0 else 0
                    tong_tien += 500000

                    return redirect(vnpay.lay_url(thong_tin=thong_tin, tong_tien=tong_tien))
        return render_template("NhanVien/QuanLyVe/CapNhatVe.html"
                               , link_tra_cuu_chuyen_bay=link_tra_cuu_chuyen_bay
                               , err=err
                               , nguoi_dung=nguoi_dung
                               , link=link
                               , chuyen_bay=chuyen_bay
                               , ds_bang_ghe=ds_bang_ghe
                               , dict_ve=dict_ve
                               , ve=ve)
    else:
        return redirect("/NhanVien")


@app.route("/NhanVien/XemThongTinNguoiDung", methods=['GET', 'POST'])
def xem_thong_tin_ca_nhan_nhan_vien():
    if current_user.is_authenticated and current_user.user_role == UserRole.NHAN_VIEN:
        sl_so_dien_thoai = request.args.get("sl_so_dien_thoai")
        if sl_so_dien_thoai and int(sl_so_dien_thoai) <= 3 and int(sl_so_dien_thoai) >= 1:
            mes = None
            sl_so_dien_thoai = int(sl_so_dien_thoai)
            ds_so_dien_thoai = dao.lay_ds_so_dien_thoai_theo_id_nguoi_dung(current_user.id_nguoi_dung)
            print(current_user.gmail)
            if request.method == 'POST':
                ten_nguoi_dung = request.form.get("ten_nguoi_dung")
                CCCD = request.form.get("CCCD")
                mat_khau = request.form.get("mat_khau").strip()
                xac_nhan = request.form.get("xac_nhan").strip()
                anh_dai_dien = request.files.get("anh_dai_dien")
                if mat_khau == xac_nhan:
                    if dao.sua_nguoi_dung(current_user.id_nguoi_dung
                                        ,ten_nguoi_dung=ten_nguoi_dung
                                        ,CCCD=CCCD
                                        ,mat_khau=mat_khau
                                        ,tai_khoan=None
                                        ,hoat_dong=True
                                        ,anh_dai_dien=anh_dai_dien):
                        kiem_tra = True
                        for so_dem in range(sl_so_dien_thoai):
                            if len(request.form.get("so_dien_thoai_"+str(so_dem)))!=10:
                                kiem_tra=False
                                break
                        if kiem_tra:
                            ds_so_dien_thoai_da_co = dao.lay_ds_so_dien_thoai(id_nguoi_dung=current_user.id_nguoi_dung)
                            dao.xoa_so_dien_thoai(id_nguoi_dung=current_user.id_nguoi_dung)
                            for so_dem in range(sl_so_dien_thoai):
                                kiem_tra = dao.tao_so_dien_thoai(id_nguoi_dung=current_user.id_nguoi_dung,so_dien_thoai=request.form.get("so_dien_thoai_"+str(so_dem)))
                                if kiem_tra:        
                                    ds_so_dien_thoai = dao.lay_ds_so_dien_thoai_theo_id_nguoi_dung(current_user.id_nguoi_dung)
                                    mes = "sửa thành công"
                                else: 
                                    if so_dem == 0:
                                        dao.them_danh_sach_so_dien_thoai(ds_so_dien_thoai=ds_so_dien_thoai_da_co)
                                    mes = "số điện thoại đã được dùng"
                                    break
                        else:
                            mes = "số điện thoại không hợp lệ"
                    else:
                        mes = "lỗi! thong tin này đã được sử dụng trước đó"
                else:
                    mes = "lỗi mật khẩu và xác nhận không trùng khớp"
            return render_template("NhanVien/XemThongTinNguoiDung.html",  mes=mes,ds_so_dien_thoai=ds_so_dien_thoai,sl_so_dien_thoai=sl_so_dien_thoai)
        else:
            return redirect("/NhanVien/XemThongTinNguoiDung?sl_so_dien_thoai="+str(dao.lay_so_luong_so_dien_thoai_theo_id_nguoi_dung(id_nguoi_dung=current_user.id_nguoi_dung)))
    else:
        return redirect("/DangNhap")


if __name__ == "__main__":
    from app.admin import *

    app.run()
