window.onload = function (){
    set_album_desc_word();
}

function set_album_desc_word(){
    let album_container = document.getElementById("album-container");
    if(!album_container)
    {
        return;
    }

    for(let node of album_container.childNodes)
    {
        if(node.nodeType !== Node.ELEMENT_NODE)
        {
            continue;
        }
        let para_elem_list =  node.getElementsByTagName('p');
        if(para_elem_list.length > 0)
        {
            let para_elem = para_elem_list[0];
            let str = para_elem.innerHTML;
            if (str.length > 100)
            {
                str = str.substring(0, 100) + "...";
                para_elem.innerHTML = str;
            }
        }
    }
}


function goto_link(link){
    window.location = link;
}

function ajax_get(url, success, error) {
    $.ajax({
            url: url,
            type: 'get',
            cache: false,
            success: success,
            error: error
        }
    );
}

function update_like_number(image_id, number) {
    let span_elem = document.getElementById('image-like-'+image_id);
    if(span_elem){
        span_elem.setAttribute("onclick", "");
        let em_elem = span_elem.getElementsByTagName('em')[0];
        em_elem.innerText = number;
    }
}

function image_like(image_id){
    let url = '/image/like/' + image_id;

    function success(data) {
        if(data['Finished']){
            update_like_number(image_id, data['like_num']);
        }
    }
    function error() {
        alert("Error! Please try it later!");
    }
    ajax_get(url, success, error);
}
