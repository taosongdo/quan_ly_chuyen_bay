import app.dao as dao
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from flask_login import current_user
import random


def lay_thong_tin(gio_hang):
    so_luong = len(gio_hang) if gio_hang else 0
    ds_don = dao.lay_ds_don(gio_hang, current_user)
    tong_tien = 0
    for don in ds_don:
        tong_tien += don["gia_ban"]
    return {'so_luong': so_luong,
            'tong_tien': tong_tien}


def tao_hoac_sua_lich_chuyen_bay(ngay_gio, thoi_gian_bay, ds_thoi_gian_dung, quy_dinh, id_chuyen_bay, so_luong_san_bay,
                                 ds_id_san_bay, ds_ghi_chu, tao_hoac_sua):
    ngay_gio = dao.lay_ngay_gio(ngay_gio=ngay_gio)
    if ngay_gio:
        thoi_gian_bay = dao.lay_thoi_gian(thoi_gian=thoi_gian_bay)
        if thoi_gian_bay:
            kiem_tra = True
            ds_thoi_gian_dung_datetime = []
            for thoi_gian_dung in ds_thoi_gian_dung:
                thoi_gian_dung_datetime = dao.lay_thoi_gian(thoi_gian=thoi_gian_dung)
                if not (thoi_gian_dung_datetime):
                    kiem_tra = False
                    break
                else:
                    ds_thoi_gian_dung_datetime.append(thoi_gian_dung_datetime)
            if kiem_tra:
                for thoi_gian_dung in ds_thoi_gian_dung_datetime:
                    if not (dao.kiem_tra_ngay_gio_theo_quy_dinh(thoi_gian_dung=thoi_gian_dung, quy_dinh=quy_dinh)):
                        kiem_tra = False
                        break
                if kiem_tra:
                    kiem_tra = dao.kiem_tra_thoi_gian_bay_theo_quy_dinh(quy_dinh=quy_dinh, thoi_gian_bay=thoi_gian_bay)
                    if kiem_tra:
                        lich_chuyen_bay = tao_hoac_sua(id_chuyen_bay, ngay_gio, thoi_gian_bay)
                        if lich_chuyen_bay:
                            for so_dem in range(so_luong_san_bay):
                                dao.tao_san_bay_trung_gian(id_san_bay=ds_id_san_bay[so_dem],
                                                           id_lich_chuyen_bay=lich_chuyen_bay.id_chuyen_bay,
                                                           ghi_chu=ds_ghi_chu[so_dem],
                                                           thoi_gian_dung=ds_thoi_gian_dung_datetime[so_dem])
                            return None
                        else:
                            return "chuyến bay đã có lịch"
                    else:
                        return "thời gian bay ít hơn so với quy định ( " + str(quy_dinh.TG_bay_toi_thieu) + " )"
                else:
                    return "thời gian không nằm trong quy định ( " + str(quy_dinh.TG_dung_toi_thieu) + " - " + str(
                        quy_dinh.TG_dung_toi_da) + " )"
            else:
                return "sai định dạng thời gian"
        else:
            return "sai định dạng thời gian"
    else:
        return "sai định dạng ngày giờ"


def lay_ds_ghe(id_chuyen_bay):
    ds_ghe = dao.lay_ds_ghe(id_chuyen_bay=id_chuyen_bay)
    ds_bang_ghe = dao.lay_ds_bang_ghe(ds_ghe=ds_ghe)
    dict_ve = dao.lay_dict_ve_theo_ghe_va_chuyen_bay()
    return ds_bang_ghe, dict_ve


def gui_email(email_nguoi_dung):
    email_he_thong = "2251052134tuan@ou.edu.vn"
    password_he_thong = "testathttt"
    noi_dung = str(random.randint(10000, 99999))

    smtp_session = smtplib.SMTP('smtp.gmail.com', 587)
    smtp_session.starttls()
    smtp_session.login(email_he_thong, password_he_thong)

    message = MIMEMultipart()
    message['From'] = email_he_thong
    message['To'] = email_nguoi_dung
    message['Subject'] = "mã xác nhận"
    message.attach(MIMEText(noi_dung, 'plain'))

    smtp_session.sendmail(from_addr=email_he_thong, to_addrs=email_nguoi_dung, msg=message.as_string())

    smtp_session.quit()
    return noi_dung
