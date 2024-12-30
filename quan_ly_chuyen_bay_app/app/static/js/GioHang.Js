id_ghe_chon = null
function chonGhe(id_ghe){
    id_ghe_chon = id_ghe
}
function themGioHang(id_chuyen_bay){
    fetch('/api/ThemGioHang', {
        'method': 'post',
        'body': JSON.stringify({
            'id_chuyen_bay': id_chuyen_bay,
            'id_ghe_chon': id_ghe_chon
        }),
        'headers': {
            'Content-Type': 'application/json'
        }
    }).then(res => res.json()).then(data=>{
        var so_luong = document.getElementById("so-luong")
        so_luong.innerHTML = `${data.so_luong}`
    })        
    
}

function xoaDon(id_ghe){
    fetch('/api/XoaDon/'+id_ghe, {
        'method': 'delete'
    }).then(res => res.json()).then(data=>{
        var soLuong = document.getElementById("so-luong")
        var tongTien = document.getElementById("tong-tien")
        var don = document.getElementById(id_ghe)
        don.style.display = "None"
        soLuong.innerHTML = `${data.so_luong}`  
        if(data.so_luong == 0)
        {
            var main = document.getElementsByTagName("main")[0]
            main.innerHTML = `<div class="alert alert-info mt-1">không có vé nào trong giỏ</div>`
        }
        else
        {
            tongTien.innerHTML = `Tổng tiền: ${parseInt(data.tong_tien).toLocaleString()} VNĐ`
        }
    })        
    
}
