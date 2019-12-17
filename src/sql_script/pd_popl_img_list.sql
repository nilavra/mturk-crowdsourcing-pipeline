BEGIN

declare vnm_ctr         int ;
declare vnm_hit_ctr     int ;
declare vnm_n_img_tot  int default 10000;  -- <<<<<<< CHANGE: how many images to crowdsource
declare vnm_img_per_hit  int default 5;
declare vvc_img         varchar(70);

declare end_cur int default false;

declare cur_img cursor for
select a.IMG
from MAI_ImgCaption.EXP_01 a  -- <<<<<<<<<<< SOURCE table
where 1=1
    -- and a.IMG not like '%VizWiz_v2_%' -- <<<<<<<< CHECK -------
  and not exists (
            select 1
            from MAI_ImgCaption.EXP_01_CROWD_RESULTS b -- <<<<<<<<<<< Crowd results SOURCE table
            where a.IMG = b.IMG
    )
order by RAND()
limit vnm_n_img_tot;

declare continue handler for not found set end_cur = true;

set vnm_ctr = 0;
set vnm_hit_ctr = 1;
truncate table MAI_ImgCaption.X_IMG;

open cur_img;

img_loop: loop

fetch cur_img into vvc_img;

if end_cur then
leave img_loop;
end if;

set vnm_ctr = vnm_ctr + 1;

insert into MAI_ImgCaption.X_IMG (IMG, HIT_CTR)
values (vvc_img, vnm_hit_ctr)
;


if vnm_ctr >= vnm_img_per_hit then

insert into MAI_ImgCaption.EXP_01_IMG_LIST -- <<<<<<<<<<< DESTINATION table
    (IMG_LIST)
select GROUP_CONCAT(a.IMG ORDER BY a.IMG ASC SEPARATOR '|')
from MAI_ImgCaption.X_IMG a
where a.HIT_CTR = vnm_hit_ctr
;

set vnm_ctr = 0;
set vnm_hit_ctr = vnm_hit_ctr + 1;

truncate table MAI_ImgCaption.X_IMG;

end if;

end loop;

-- insert leftover rows in X_IMG
if (exists (select 1 from MAI_ImgCaption.X_IMG)) then

insert into MAI_ImgCaption.EXP_01_IMG_LIST -- <<<<<<<<<<< DESTINATION table
    (IMG_LIST)
select GROUP_CONCAT(a.IMG ORDER BY a.IMG ASC SEPARATOR '|')
from MAI_ImgCaption.X_IMG a
where a.HIT_CTR = vnm_hit_ctr
;

end if;

truncate table MAI_ImgCaption.X_IMG;

commit;

END