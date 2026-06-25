from odoo import models, fields


class ResCompany(models.Model):
    _inherit = 'res.company'

    # --- Entity classification ---------------------------------------------------
    entity_kind = fields.Selection([
        ('association', 'Association'),
        ('organization', 'Organization'),
        ('institution', 'Institution'),
    ], string='Type', tracking=True,
       help='Classify this company as an Association, Organization, or Institution.')

    org_status = fields.Selection([
        ('active', 'Active'),
        ('pending', 'Pending'),
        ('registered', 'Registered'),
        ('suspended', 'Suspended'),
        ('inactive', 'Inactive'),
    ], string='Organization Status', default='active', tracking=True)

    # --- Usage domains -----------------------------------------------------------
    is_sports = fields.Boolean(string='Used in Sports', default=False, tracking=True)
    is_arts = fields.Boolean(string='Used in Arts', default=False, tracking=True)
    is_youth = fields.Boolean(string='Used in Youth', default=False, tracking=True)

    # --- Domain-specific descriptors ---------------------------------------------
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

    # --- Additional registry fields ----------------------------------------------
    registration_number = fields.Char(string='Registration Number', tracking=True)
    org_code = fields.Char(string='Code', tracking=True,
                           help='Short code or acronym for this association/organization.')
    org_description = fields.Text(string='Description')
