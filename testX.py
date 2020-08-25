
from datetime import datetime
from lib_bittrex3 import bittrex_orders_closed_get
from common import logger, log_file_write
from lib_db import db
from common import dec

lib_display_lvl = 0
lib_debug_lvl   = 0

#updated to v3, still testing
def db_orders_tbl_ins(od, display_lvl=lib_display_lvl, debug_lvl=lib_debug_lvl):
	func_name = "lib_db.db_orders_tbl_ins(od, display_lvl=" + str(display_lvl) + ", debug_lvl=" + str(debug_lvl) + ")"
	if debug_lvl >= 1: print('')
	if debug_lvl >= 1: print('')
	if debug_lvl >= 1: print(func_name)

#use ctb;
#drop table if exists order_data;
#create table if not exists order_data
#(
#	seqid                         integer not null auto_increment
#	, tp                          varchar(255)
#	, tpf                         varchar(255)
#	, mc                          varchar(255)
#	, tc                          varchar(255)
#	, bs                          varchar(4)
#	, cnt                         decimal(20,8)
#	, prc                         decimal(20,8)
#	, amt                         decimal(20,8)
#	, fee                         decimal(20,8)
#	, tot                         decimal(20,8)
#	, od_id                       varchar(255)
#	, od_marketSymbol             varchar(21)
#	, od_direction                varchar(4)
#	, od_type                     varchar(20)
#	, od_quantity                 decimal(20,8)
#	, od_limit                    decimal(20,8)
#	, od_ceiling                  decimal(20,8)
#	, od_timeinforce              varchar(50)
#	, od_clientorderid            varchar(255)
#	, od_fillquantity             decimal(20,8)
#	, od_commission               decimal(20,8)
#	, od_proceeds                 decimal(20,8)
#	, od_status                   varchar(255)
#	, od_created                  datetime
#	, od_updated                  datetime
#	, od_closed                   datetime
#	, od_cancelordertype          varchar(20)
#	, od_cancelorderuuid          varchar(255)
#	, primary key (seqid)
#	, index order_data_idx (seqid asc)
#);

	od_id                        = None
	if 'id' in od:
		od_id = od['id']
	if debug_lvl >= 1: print('od_id                    : ' + str(od_id))

	od_marketsymbol              = None
	if 'marketSymbol' in od:
		od_marketsymbol = od['marketSymbol']
	if debug_lvl >= 1: print('od_marketsymbol          : ' + str(od_marketsymbol))

	od_direction                 = None
	if 'direction' in od:
		od_direction = od['direction']
	if debug_lvl >= 1: print('od_direction             : ' + str(od_direction))

	od_type                      = None
	if 'type' in od:
		od_type = od['type']
	if debug_lvl >= 1: print('od_type                  : ' + str(od_type))

	od_quantity                  = None
	if 'quantity' in od:
		if od['quantity'] :
			od_quantity = od['quantity']
			if od_quantity == 'None':
				od_quantity = None
	if debug_lvl >= 1: print('od_quantity              : ' + str(od_quantity))

	od_limit                     = None
	if 'limit' in od:
		if od['limit'] :
			od_limit = od['limit']
			if od_limit == 'None':
				od_limit = None
	if debug_lvl >= 1: print('od_limit                 : ' + str(od_limit))

	od_ceiling                   = None
	if 'ceiling' in od:
		if od['ceiling'] :
			od_ceiling = od['ceiling']
			if od_ceiling == 'None':
				od_ceiling = None
	if debug_lvl >= 1: print('od_ceiling               : ' + str(od_ceiling))

	od_timeinforce               = None
	if 'timeInForce' in od:
		od_timeinforce = od['timeInForce']
	if debug_lvl >= 1: print('od_timeinforce           : ' + str(od_timeinforce))

	od_clientorderid             = None
	if 'clientOrderId' in od:
		if od['clientOrderId'] :
			od_clientorderid = od['clientOrderId']
			if od_clientorderid == 'None':
				od_clientorderid = None
	if debug_lvl >= 1: print('od_clientorderid         : ' + str(od_clientorderid))

	od_fillquantity              = None
	if 'fillQuantity' in od:
		od_fillquantity = od['fillQuantity']
	if debug_lvl >= 1: print('od_fillquantity          : ' + str(od_fillquantity))

	od_commission                = None
	if 'commission' in od:
		od_commission = od['commission']
	if debug_lvl >= 1: print('od_commission            : ' + str(od_commission))

	od_proceeds                  = None
	if 'proceeds' in od:
		od_proceeds = od['proceeds']
		if od_proceeds == 'None':
			od_proceeds = None
	if debug_lvl >= 1: print('od_proceeds              : ' + str(od_proceeds))

	od_status                    = None
	if 'status' in od:
		od_status = od['status']
	if debug_lvl >= 1: print('od_status                : ' + str(od_status))

	od_created                   = None
	if 'createdAt' in od:
		if od['createdAt'] :
			od_created = datetime.strptime(od['createdAt'][:19], '%Y-%m-%dT%H:%M:%S')
	if debug_lvl >= 1: print('od_created               : ' + str(od_created))

	od_updated                   = None
	if 'updatedAt' in od:
		if od['updatedAt'] :
			od_updated = datetime.strptime(od['updatedAt'][:19], '%Y-%m-%dT%H:%M:%S')
	if debug_lvl >= 1: print('od_updated               : ' + str(od_updated))

	od_closed                    = None
	if 'closedAt' in od:
		if od['closedAt'] :
			od_closed = datetime.strptime(od['closedAt'][:19], '%Y-%m-%dT%H:%M:%S')
	if debug_lvl >= 1: print('od_closed                : ' + str(od_closed))

	od_cancelordertype           = None
	od_cancelorderuuid           = None
	if 'orderToCancel' in od:
		otc = od['orderToCancel']
		if 'type' in otc:
			if od['cancelordertype'] :
				od_cancelordertype = otc['type']
		if 'id' in otc:
			if od['cancelorderid'] :
				od_cancelorderid = otc['id']
	if debug_lvl >= 1: print('od_cancelordertype       : ' + str(od_cancelordertype))
	if debug_lvl >= 1: print('od_cancelorderuuid       : ' + str(od_cancelorderuuid))

	tpf = od_marketsymbol
	mc  = tpf.split('-')[1]
	tc  = tpf.split('-')[0]
	tp  = mc + '-' + tc
	bs  = od_direction.lower()
	cnt = dec(od_fillquantity)
	amt = dec(od_proceeds)
	prc = round(amt / cnt, 8)
	fee = dec(od_commission)
	if bs == 'buy':
		if amt > 0: amt = amt * -1
		if fee > 0: fee = fee * -1
		tot = amt + fee
	if bs == 'sell':
		if cnt > 0: cnt = cnt * -1
		if fee > 0: fee = fee * -1
		tot = amt + fee

	if debug_lvl >= 1: print('tp                       : ' + str(tp))
	if debug_lvl >= 1: print('tpf                      : ' + str(tpf))
	if debug_lvl >= 1: print('mc                       : ' + str(mc))
	if debug_lvl >= 1: print('tc                       : ' + str(tc))
	if debug_lvl >= 1: print('bs                       : ' + str(bs))
	if debug_lvl >= 1: print('cnt                      : ' + str(cnt))
	if debug_lvl >= 1: print('prc                      : ' + str(prc))
	if debug_lvl >= 1: print('amt                      : ' + str(amt))
	if debug_lvl >= 1: print('fee                      : ' + str(fee))
	if debug_lvl >= 1: print('tot                      : ' + str(tot))

	if debug_lvl >= 1: print('')
	if debug_lvl >= 1: print('')

	try:
		s= ""
		s += "insert into order_data ("
		s += "    tp "
		s += "  , tpf "
		s += "  , mc "
		s += "  , tc "
		s += "  , bs "
		s += "  , cnt "
		s += "  , prc "
		s += "  , amt "
		s += "  , fee "
		s += "  , tot "

		s += "  , od_id "
		s += "  , od_marketsymbol "
		s += "  , od_direction "
		s += "  , od_type "
		s += "  , od_quantity "
		s += "  , od_limit "
		s += "  , od_ceiling "
		s += "  , od_timeinforce "
		s += "  , od_clientorderid "
		s += "  , od_fillquantity "

		s += "  , od_commission "
		s += "  , od_proceeds "
		s += "  , od_status "
		s += "  , od_created "
		s += "  , od_updated "
		s += "  , od_closed "
		s += "  , od_cancelordertype "
		s += "  , od_cancelorderuuid "
		s += "  ) values ( "
		s += "    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s "
		s += "  , %s, %s, %s, %s, %s, %s, %s, %s, %s, %s "
		s += "  , %s, %s, %s, %s, %s, %s, %s, %s "
		s += "   )"
		s += "  ON DUPLICATE KEY update "
		s += "    tp                 = values(tp) "
		s += "  , tpf                = values(tpf) "
		s += "  , mc                 = values(mc) "
		s += "  , tc                 = values(tc) "
		s += "  , bs                 = values(bs) "
		s += "  , cnt                = values(cnt) "
		s += "  , prc                = values(prc) "
		s += "  , amt                = values(amt) "
		s += "  , fee                = values(fee) "
		s += "  , tot                = values(tot) "

		s += "  , od_id              = values(od_id) "
		s += "  , od_marketsymbol    = values(od_marketsymbol) "
		s += "  , od_direction       = values(od_direction) "
		s += "  , od_type            = values(od_type) "
		s += "  , od_quantity        = values(od_quantity) "
		s += "  , od_limit           = values(od_limit) "
		s += "  , od_ceiling         = values(od_ceiling) "
		s += "  , od_timeinforce     = values(od_timeinforce) "
		s += "  , od_clientorderid   = values(od_clientorderid) "
		s += "  , od_fillquantity    = values(od_fillquantity) "

		s += "  , od_commission      = values(od_commission) "
		s += "  , od_proceeds        = values(od_proceeds) "
		s += "  , od_status          = values(od_status) "
		s += "  , od_created         = values(od_created) "
		s += "  , od_updated         = values(od_updated) "
		s += "  , od_closed          = values(od_closed) "
		s += "  , od_cancelordertype = values(od_cancelordertype) "
		s += "  , od_cancelorderuuid = values(od_cancelorderuuid) "
		v = (tp
			, tpf
			, mc
			, tc
			, bs
			, cnt
			, prc
			, amt
			, fee
			, tot
			, od_id
			, od_marketsymbol
			, od_direction
			, od_type
			, od_quantity
			, od_limit
			, od_ceiling
			, od_timeinforce
			, od_clientorderid
			, od_fillquantity
			, od_commission
			, od_proceeds
			, od_status
			, od_created
			, od_updated
			, od_closed
			, od_cancelordertype
			, od_cancelorderuuid)
		seq_id = db.insert_one(s, v)
	except Exception:
		print(func_name + 'errored.')
		logger.exception(Exception)
		print(od)
		print(s)
		print(v)
		play_beep()
		raise
		exit()

	return seq_id



#exit()

display_lvl = 1
debug_lvl   = 1

ol = bittrex_orders_closed_get()

filename = 'data\order_data.txt'
log_file_write(filename, ol)

for od in ol.values():
	db_orders_tbl_ins(od)



