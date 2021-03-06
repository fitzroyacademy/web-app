"""initial migration

Revision ID: 0ba154a101c9
Revises: 
Create Date: 2020-05-30 14:46:10.180556

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0ba154a101c9'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('institutes',
    sa.Column('_is_deleted', sa.Boolean(), nullable=True),
    sa.Column('created_on', sa.DateTime(), nullable=True),
    sa.Column('last_updated', sa.DateTime(), nullable=True),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=True),
    sa.Column('description', sa.String(length=140), nullable=True),
    sa.Column('cover_image', sa.String(), nullable=True),
    sa.Column('logo', sa.String(), nullable=True),
    sa.Column('slug', sa.String(length=50), nullable=True),
    sa.Column('for_who', sa.String(), nullable=True),
    sa.Column('location', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('slug')
    )
    op.create_table('programs',
    sa.Column('_is_deleted', sa.Boolean(), nullable=True),
    sa.Column('created_on', sa.DateTime(), nullable=True),
    sa.Column('last_updated', sa.DateTime(), nullable=True),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=True),
    sa.Column('slug', sa.String(length=50), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('slug')
    )
    op.create_table('users',
    sa.Column('_is_deleted', sa.Boolean(), nullable=True),
    sa.Column('created_on', sa.DateTime(), nullable=True),
    sa.Column('last_updated', sa.DateTime(), nullable=True),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=50), nullable=True),
    sa.Column('first_name', sa.String(), nullable=True),
    sa.Column('last_name', sa.String(), nullable=True),
    sa.Column('email', sa.String(), nullable=True),
    sa.Column('phone_number', sa.String(length=15), nullable=True),
    sa.Column('dob', sa.Date(), nullable=True),
    sa.Column('password_hash', sa.String(length=128), nullable=True),
    sa.Column('profile_picture', sa.String(), nullable=True),
    sa.Column('bio', sa.String(), nullable=True),
    sa.Column('super_admin', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email'),
    sa.UniqueConstraint('username')
    )
    op.create_table('courses',
    sa.Column('_is_deleted', sa.Boolean(), nullable=True),
    sa.Column('created_on', sa.DateTime(), nullable=True),
    sa.Column('last_updated', sa.DateTime(), nullable=True),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(), nullable=True),
    sa.Column('picture', sa.String(), nullable=True),
    sa.Column('cover_image', sa.String(), nullable=True),
    sa.Column('order', sa.Integer(), nullable=True),
    sa.Column('year', sa.Date(), nullable=True),
    sa.Column('course_code', sa.String(length=16), nullable=True),
    sa.Column('paid', sa.Boolean(), nullable=True),
    sa.Column('amount', sa.Integer(), nullable=True),
    sa.Column('guest_access', sa.Boolean(), nullable=True),
    sa.Column('language', sa.String(length=2), nullable=True),
    sa.Column('slug', sa.String(length=50), nullable=True),
    sa.Column('draft', sa.Boolean(), nullable=True),
    sa.Column('target_audience', sa.String(), nullable=True),
    sa.Column('skill_level', sa.String(), nullable=True),
    sa.Column('info', sa.String(), nullable=True),
    sa.Column('visibility', sa.String(length=16), nullable=True),
    sa.Column('summary_html', sa.String(), nullable=True),
    sa.Column('workload_summary', sa.String(), nullable=True),
    sa.Column('workload_title', sa.String(), nullable=True),
    sa.Column('workload_subtitle', sa.String(), nullable=True),
    sa.Column('program_id', sa.Integer(), nullable=True),
    sa.Column('institute_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['institute_id'], ['institutes.id'], ),
    sa.ForeignKeyConstraint(['program_id'], ['programs.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('course_code'),
    sa.UniqueConstraint('slug')
    )
    op.create_table('custom_setting',
    sa.Column('_is_deleted', sa.Boolean(), nullable=True),
    sa.Column('created_on', sa.DateTime(), nullable=True),
    sa.Column('last_updated', sa.DateTime(), nullable=True),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('key', sa.String(length=16), nullable=True),
    sa.Column('value', sa.String(length=64), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('user_id', 'key', name='_user_custom_setting')
    )
    op.create_table('users_institutes',
    sa.Column('_is_deleted', sa.Boolean(), nullable=True),
    sa.Column('created_on', sa.DateTime(), nullable=True),
    sa.Column('last_updated', sa.DateTime(), nullable=True),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('institute_id', sa.Integer(), nullable=True),
    sa.Column('access_level', sa.Enum('admin', 'manager', 'teacher', name='institutepermissionenum'), nullable=True),
    sa.ForeignKeyConstraint(['institute_id'], ['institutes.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('users_preferences',
    sa.Column('_is_deleted', sa.Boolean(), nullable=True),
    sa.Column('created_on', sa.DateTime(), nullable=True),
    sa.Column('last_updated', sa.DateTime(), nullable=True),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('preference', sa.Integer(), nullable=True),
    sa.Column('toggled', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('users_programs',
    sa.Column('_is_deleted', sa.Boolean(), nullable=True),
    sa.Column('created_on', sa.DateTime(), nullable=True),
    sa.Column('last_updated', sa.DateTime(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('program_id', sa.Integer(), nullable=False),
    sa.Column('access_level', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['program_id'], ['programs.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('user_id', 'program_id')
    )
    op.create_table('courses_translated',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('course_id', sa.Integer(), nullable=True),
    sa.Column('title', sa.String(), nullable=True),
    sa.Column('language', sa.String(length=2), nullable=True),
    sa.ForeignKeyConstraint(['course_id'], ['courses.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('lessons',
    sa.Column('_is_deleted', sa.Boolean(), nullable=True),
    sa.Column('created_on', sa.DateTime(), nullable=True),
    sa.Column('last_updated', sa.DateTime(), nullable=True),
    sa.Column('order', sa.Integer(), nullable=True),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(), nullable=True),
    sa.Column('active', sa.Boolean(), nullable=True),
    sa.Column('language', sa.String(length=2), nullable=True),
    sa.Column('slug', sa.String(length=50), nullable=True),
    sa.Column('cover_image', sa.String(), nullable=True),
    sa.Column('description', sa.String(length=140), nullable=True),
    sa.Column('further_reading', sa.String(), nullable=True),
    sa.Column('course_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['course_id'], ['courses.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('users_courses',
    sa.Column('_is_deleted', sa.Boolean(), nullable=True),
    sa.Column('created_on', sa.DateTime(), nullable=True),
    sa.Column('last_updated', sa.DateTime(), nullable=True),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('course_id', sa.Integer(), nullable=True),
    sa.Column('access_level', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['course_id'], ['courses.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('course_id', 'user_id', name='_course_user_enrollment')
    )
    op.create_table('_lesson_user_enrollment',
    sa.Column('users_courses_id', sa.Integer(), nullable=True),
    sa.Column('lessons_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['lessons_id'], ['lessons.id'], ),
    sa.ForeignKeyConstraint(['users_courses_id'], ['users_courses.id'], )
    )
    op.create_table('lesson_qa',
    sa.Column('_is_deleted', sa.Boolean(), nullable=True),
    sa.Column('created_on', sa.DateTime(), nullable=True),
    sa.Column('last_updated', sa.DateTime(), nullable=True),
    sa.Column('order', sa.Integer(), nullable=True),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('question', sa.String(), nullable=True),
    sa.Column('answer', sa.String(), nullable=True),
    sa.Column('lesson_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['lesson_id'], ['lessons.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('lesson_resources',
    sa.Column('_is_deleted', sa.Boolean(), nullable=True),
    sa.Column('created_on', sa.DateTime(), nullable=True),
    sa.Column('last_updated', sa.DateTime(), nullable=True),
    sa.Column('order', sa.Integer(), nullable=True),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(), nullable=True),
    sa.Column('url', sa.String(), nullable=True),
    sa.Column('type', sa.Enum('google_doc', 'google_sheet', 'google_slide', 'google_drawing', 'youtube', 'pdf', 'file_generic', 'image', name='resourcetypeenum'), nullable=True),
    sa.Column('featured', sa.Boolean(), nullable=True),
    sa.Column('language', sa.String(length=2), nullable=True),
    sa.Column('slug', sa.String(length=50), nullable=True),
    sa.Column('description', sa.String(), nullable=True),
    sa.Column('anonymous_views', sa.Integer(), nullable=True),
    sa.Column('lesson_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['lesson_id'], ['lessons.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('lesson_segments',
    sa.Column('_is_deleted', sa.Boolean(), nullable=True),
    sa.Column('created_on', sa.DateTime(), nullable=True),
    sa.Column('last_updated', sa.DateTime(), nullable=True),
    sa.Column('order', sa.Integer(), nullable=True),
    sa.Column('survey_type', sa.Enum('plain_text', 'emoji', 'points_scale', name='surveytypeenum'), nullable=True),
    sa.Column('questions_template', sa.String(), nullable=True),
    sa.Column('answer_template', sa.String(), nullable=True),
    sa.Column('barrier', sa.Enum('normal', 'barrier', 'hard_barrier', 'hidden', 'paid', 'login', name='segmentbarrierenum'), nullable=True),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('type', sa.Enum('video', 'text', 'survey', name='segmenttype'), nullable=True),
    sa.Column('video_type', sa.Enum('standard', 'resources', 'practical', 'interview', 'case', 'story', 'bonus', name='videotypeenum'), nullable=True),
    sa.Column('title', sa.String(), nullable=True),
    sa.Column('text', sa.String(), nullable=True),
    sa.Column('duration_seconds', sa.Integer(), nullable=True),
    sa.Column('external_id', sa.String(), nullable=True),
    sa.Column('url', sa.String(), nullable=True),
    sa.Column('language', sa.String(length=2), nullable=True),
    sa.Column('slug', sa.String(length=50), nullable=True),
    sa.Column('_thumbnail', sa.String(), nullable=True),
    sa.Column('lesson_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['lesson_id'], ['lessons.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('lesson_id', 'slug', name='_lesson_segment_uc')
    )
    op.create_table('lessons_translated',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('lesson_id', sa.Integer(), nullable=True),
    sa.Column('title', sa.String(), nullable=True),
    sa.Column('duration_seconds', sa.Integer(), nullable=True),
    sa.Column('url', sa.String(), nullable=True),
    sa.Column('language', sa.String(length=2), nullable=True),
    sa.ForeignKeyConstraint(['lesson_id'], ['lessons.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('lesson_segments_survey_response',
    sa.Column('_is_deleted', sa.Boolean(), nullable=True),
    sa.Column('created_on', sa.DateTime(), nullable=True),
    sa.Column('last_updated', sa.DateTime(), nullable=True),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('answers', sa.String(), nullable=True),
    sa.Column('segment_id', sa.Integer(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['segment_id'], ['lesson_segments.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('segment_id', 'user_id', name='_segment_survey_response_user_uc')
    )
    op.create_table('lesson_segments_translated',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('segment_id', sa.Integer(), nullable=True),
    sa.Column('title', sa.String(), nullable=True),
    sa.Column('duration_seconds', sa.Integer(), nullable=True),
    sa.Column('url', sa.String(), nullable=True),
    sa.Column('language', sa.String(length=2), nullable=True),
    sa.ForeignKeyConstraint(['segment_id'], ['lesson_segments.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('resource_user_access',
    sa.Column('_is_deleted', sa.Boolean(), nullable=True),
    sa.Column('created_on', sa.DateTime(), nullable=True),
    sa.Column('last_updated', sa.DateTime(), nullable=True),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('resource_id', sa.Integer(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('access_date', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['resource_id'], ['lesson_resources.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('segment_user_progress',
    sa.Column('_is_deleted', sa.Boolean(), nullable=True),
    sa.Column('created_on', sa.DateTime(), nullable=True),
    sa.Column('last_updated', sa.DateTime(), nullable=True),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('progress', sa.Integer(), nullable=True),
    sa.Column('segment_id', sa.Integer(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['segment_id'], ['lesson_segments.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('segment_user_progress')
    op.drop_table('resource_user_access')
    op.drop_table('lesson_segments_translated')
    op.drop_table('lesson_segments_survey_response')
    op.drop_table('lessons_translated')
    op.drop_table('lesson_segments')
    op.drop_table('lesson_resources')
    op.drop_table('lesson_qa')
    op.drop_table('_lesson_user_enrollment')
    op.drop_table('users_courses')
    op.drop_table('lessons')
    op.drop_table('courses_translated')
    op.drop_table('users_programs')
    op.drop_table('users_preferences')
    op.drop_table('users_institutes')
    op.drop_table('custom_setting')
    op.drop_table('courses')
    op.drop_table('users')
    op.drop_table('programs')
    op.drop_table('institutes')
    # ### end Alembic commands ###
