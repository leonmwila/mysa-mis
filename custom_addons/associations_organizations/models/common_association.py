from odoo import models, fields


class CommonAssociation(models.Model):
    _name = 'common.association'
    _description = 'Common Association or Organization'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name'

    name = fields.Char(string='Name', required=True, tracking=True)
    code = fields.Char(string='Code', copy=False, tracking=True)

    entity_kind = fields.Selection([
        ('association', 'Association'),
        ('organization', 'Organization'),
    ], string='Type', required=True, default='association', tracking=True)

    is_sports = fields.Boolean(string='Used in Sports', default=False, tracking=True)
    is_arts = fields.Boolean(string='Used in Arts', default=False, tracking=True)
    is_youth = fields.Boolean(string='Used in Youth', default=False, tracking=True)

    # Domain-specific descriptors
    sports_type = fields.Selection([
        ('football', 'Football'),
        ('basketball', 'Basketball'),
        ('volleyball', 'Volleyball'),
        ('athletics', 'Athletics'),
        ('swimming', 'Swimming'),
        ('boxing', 'Boxing'),
        ('tennis', 'Tennis'),
        ('netball', 'Netball'),
        ('cricket', 'Cricket'),
        ('rugby', 'Rugby'),
        ('martial_arts', 'Martial Arts'),
        ('cycling', 'Cycling'),
        ('badminton', 'Badminton'),
        ('other', 'Other'),
    ], string='Primary Sport')

    art_focus = fields.Selection([
        ('multi_arts', 'Multi-Arts'),
        ('dance', 'Dance'),
        ('music', 'Music'),
        ('visual_arts', 'Visual Arts'),
        ('theater', 'Theater'),
        ('film', 'Film'),
        ('literature', 'Literature'),
        ('digital_arts', 'Digital Arts'),
        ('traditional_arts', 'Traditional Arts'),
        ('other', 'Other'),
    ], string='Artistic Focus')

    organization_type = fields.Selection([
        ('youth_club', 'Youth Club'),
        ('sports_club', 'Youth Sports Club'),
        ('cultural_group', 'Cultural Group'),
        ('church_group', 'Church Youth Group'),
        ('school_group', 'School Youth Group'),
        ('community_group', 'Community Youth Group'),
        ('cooperative', 'Youth Cooperative'),
        ('cbo', 'Community Based Organization'),
        ('ngo', 'Non-Governmental Organization'),
        ('other', 'Other'),
    ], string='Organization Type')

    status = fields.Selection([
        ('active', 'Active'),
        ('pending', 'Pending'),
        ('registered', 'Registered'),
        ('suspended', 'Suspended'),
        ('inactive', 'Inactive'),
    ], string='Status', default='active', tracking=True)

    contact_person = fields.Char(string='Contact Person')
    phone = fields.Char(string='Phone')
    email = fields.Char(string='Email')
    website = fields.Char(string='Website')
    address = fields.Text(string='Address')
    registration_number = fields.Char(string='Registration Number')
    description = fields.Text(string='Description')
    active = fields.Boolean(string='Active', default=True, tracking=True)
    approved_by_id = fields.Many2one('res.users', string='Approved/Certified By', readonly=True, tracking=True)
    approved_date = fields.Datetime(string='Approved/Certified On', readonly=True, tracking=True)

    legacy_model = fields.Char(string='Legacy Model', readonly=True, index=True)
    legacy_res_id = fields.Integer(string='Legacy Record ID', readonly=True, index=True)

    _sql_constraints = [
        (
            'common_association_legacy_unique',
            'unique(legacy_model, legacy_res_id)',
            'Legacy model and record mapping must be unique.',
        ),
    ]

    def init(self):
        super().init()
        self._ensure_core_columns()
        self._ensure_relation_tables()
        self._migrate_legacy_records()

    def _ensure_core_columns(self):
        cr = self.env.cr
        cr.execute(
            '''ALTER TABLE IF EXISTS "common_association"
               ADD COLUMN IF NOT EXISTS "legacy_model" VARCHAR'''
        )
        cr.execute(
            '''ALTER TABLE IF EXISTS "common_association"
               ADD COLUMN IF NOT EXISTS "legacy_res_id" INTEGER'''
        )
        cr.execute(
            '''CREATE INDEX IF NOT EXISTS "common_association_legacy_model_idx"
               ON "common_association" ("legacy_model")'''
        )
        cr.execute(
            '''CREATE INDEX IF NOT EXISTS "common_association_legacy_res_id_idx"
               ON "common_association" ("legacy_res_id")'''
        )

    def _ensure_relation_tables(self):
        cr = self.env.cr
        relation_specs = [
            ('artist_zone_common_association_rel', 'zone_id', 'association_id'),
            ('sports_zone_common_association_rel', 'zone_id', 'association_id'),
            ('youth_zone_common_association_rel', 'zone_id', 'association_id'),
            ('artist_common_association_rel', 'artist_id', 'association_id'),
            ('sports_athlete_common_association_rel', 'athlete_id', 'association_id'),
            ('youth_common_association_rel', 'youth_id', 'association_id'),
        ]

        for table_name, left_col, right_col in relation_specs:
            cr.execute(
                f'''CREATE TABLE IF NOT EXISTS "{table_name}" (
                    "{left_col}" INTEGER NOT NULL,
                    "{right_col}" INTEGER NOT NULL
                )'''
            )
            cr.execute(
                f'''ALTER TABLE "{table_name}"
                    ADD COLUMN IF NOT EXISTS "{left_col}" INTEGER'''
            )
            cr.execute(
                f'''ALTER TABLE "{table_name}"
                    ADD COLUMN IF NOT EXISTS "{right_col}" INTEGER'''
            )
            cr.execute(
                f'''CREATE UNIQUE INDEX IF NOT EXISTS
                    "{table_name}_{left_col}_{right_col}_uniq"
                    ON "{table_name}" ("{left_col}", "{right_col}")'''
            )
            cr.execute(
                f'''CREATE INDEX IF NOT EXISTS
                    "{table_name}_{right_col}_idx"
                    ON "{table_name}" ("{right_col}")'''
            )

    def _get_or_create_common(self, legacy_model, legacy_rec, values):
        common = self.search([
            ('legacy_model', '=', legacy_model),
            ('legacy_res_id', '=', legacy_rec.id),
        ], limit=1)
        if common:
            common.write(values)
            return common
        values.update({
            'legacy_model': legacy_model,
            'legacy_res_id': legacy_rec.id,
        })
        return self.create(values)

    def _migrate_legacy_records(self):
        env = self.env
        mapping = {}

        if 'sports.association' in env:
            for record in env['sports.association'].search([]):
                common = self._get_or_create_common('sports.association', record, {
                    'name': record.name,
                    'code': record.short_name or record.registration_number,
                    'entity_kind': 'association',
                    'is_sports': True,
                    'sports_type': record.sports_type,
                    'status': record.status if record.status in dict(self._fields['status'].selection) else 'active',
                    'contact_person': record.contact_person,
                    'phone': record.phone,
                    'email': record.email,
                    'address': record.address,
                    'registration_number': record.registration_number,
                    'description': record.description,
                    'active': record.active,
                })
                mapping[('sports.association', record.id)] = common.id

        if 'artist.association' in env:
            for record in env['artist.association'].search([]):
                status_map = {
                    'registered': 'registered',
                    'pending': 'pending',
                    'inactive': 'inactive',
                    'suspended': 'suspended',
                    'informal': 'active',
                    'dissolved': 'inactive',
                    'active': 'active',
                }
                common = self._get_or_create_common('artist.association', record, {
                    'name': record.name,
                    'code': record.acronym or record.association_id,
                    'entity_kind': 'association',
                    'is_arts': True,
                    'art_focus': record.art_focus,
                    'status': status_map.get(record.status or record.legal_status, 'active'),
                    'contact_person': record.president_id.name if record.president_id else False,
                    'phone': record.phone,
                    'email': record.email,
                    'website': record.website,
                    'address': record.headquarters_address,
                    'registration_number': record.registration_number,
                    'description': record.description,
                    'active': record.status != 'dissolved',
                })
                mapping[('artist.association', record.id)] = common.id

        if 'youth.organization' in env:
            for record in env['youth.organization'].search([]):
                status_map = {
                    'registered': 'registered',
                    'pending': 'pending',
                    'certified': 'registered',
                    'suspended': 'suspended',
                    'deregistered': 'inactive',
                }
                common = self._get_or_create_common('youth.organization', record, {
                    'name': record.name,
                    'code': record.organization_id,
                    'entity_kind': 'organization',
                    'is_youth': True,
                    'organization_type': record.organization_type,
                    'status': status_map.get(record.registration_status, 'active'),
                    'contact_person': record.chairperson_id.name if record.chairperson_id else False,
                    'phone': record.phone,
                    'email': record.email,
                    'website': record.website,
                    'address': record.physical_address,
                    'registration_number': record.registration_number,
                    'description': record.description,
                    'active': record.active,
                })
                mapping[('youth.organization', record.id)] = common.id

        if 'artist.artist' in env and 'artist.association' in env:
            for artist in env['artist.artist'].search([('association_ids', '!=', False)]):
                common_ids = [
                    mapping.get(('artist.association', assoc.id))
                    for assoc in artist.association_ids
                ]
                common_ids = [association_id for association_id in common_ids if association_id]
                if common_ids:
                    artist.common_association_ids = [(6, 0, list(set(artist.common_association_ids.ids + common_ids)))]

        if 'sports.athlete' in env and 'sports.association' in env:
            for athlete in env['sports.athlete'].search([('association_ids', '!=', False)]):
                common_ids = [
                    mapping.get(('sports.association', assoc.id))
                    for assoc in athlete.association_ids
                ]
                common_ids = [association_id for association_id in common_ids if association_id]
                if common_ids:
                    athlete.common_association_ids = [(6, 0, list(set(athlete.common_association_ids.ids + common_ids)))]

        if 'youth.youth' in env and 'youth.organization' in env:
            for youth in env['youth.youth'].search([('organization_ids', '!=', False)]):
                common_ids = [
                    mapping.get(('youth.organization', org.id))
                    for org in youth.organization_ids
                ]
                common_ids = [association_id for association_id in common_ids if association_id]
                if common_ids:
                    youth.common_association_ids = [(6, 0, list(set(youth.common_association_ids.ids + common_ids)))]

        if 'youth.program' in env and 'youth.organization' in env:
            for program in env['youth.program'].search([('organizing_body_id', '!=', False)]):
                mapped_id = mapping.get(('youth.organization', program.organizing_body_id.id))
                if mapped_id and not program.common_organizing_body_id:
                    program.common_organizing_body_id = mapped_id

        if 'sports.team' in env and 'sports.association' in env:
            for team in env['sports.team'].search([('association_id', '!=', False)]):
                mapped_id = mapping.get(('sports.association', team.association_id.id))
                if mapped_id and not team.common_association_id:
                    team.common_association_id = mapped_id

        if 'artist.band' in env and 'artist.association' in env:
            for band in env['artist.band'].search([('association_id', '!=', False)]):
                mapped_id = mapping.get(('artist.association', band.association_id.id))
                if mapped_id and not band.common_association_id:
                    band.common_association_id = mapped_id

    def action_approve_certify(self):
        for record in self:
            record.write({
                'status': 'registered',
                'active': True,
                'approved_by_id': self.env.user.id,
                'approved_date': fields.Datetime.now(),
            })
