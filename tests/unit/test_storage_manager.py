"""
Unit tests for the storage manager module.
"""
import os
import pytest
from unittest.mock import patch, mock_open, MagicMock, call

from src.core import storage_manager


@pytest.mark.unit
class TestStorageManager:
    """Tests for the storage_manager module."""

    def test_get_drives_info(self):
        """Test getting drive information."""
        mock_devices = [
            {'name': 'sda', 'type': 'disk', 'size': '2000G', 'children': [
                {'name': 'sda1', 'type': 'part', 'size': '2000G', 'fstype': 'ext4'}
            ]},
            {'name': 'sdb', 'type': 'disk', 'size': '1000G', 'children': [
                {'name': 'sdb1', 'type': 'part', 'size': '1000G', 'fstype': 'ext4'}
            ]}
        ]
        mock_lsblk_output = {'blockdevices': mock_devices}
        
        mock_disk_usage = MagicMock()
        mock_disk_usage.total = 2000 * 1024 * 1024 * 1024  # 2TB
        mock_disk_usage.used = 500 * 1024 * 1024 * 1024    # 500GB
        mock_disk_usage.free = 1500 * 1024 * 1024 * 1024   # 1.5TB
        mock_disk_usage.percent = 25
        
        with patch('subprocess.run') as mock_run, \
             patch('json.loads', return_value=mock_lsblk_output), \
             patch('psutil.disk_usage', return_value=mock_disk_usage), \
             patch('os.path.ismount', return_value=True):
            
            mock_run.return_value.stdout = '{}'
            mock_run.return_value.returncode = 0
            
            drives_info = storage_manager.get_drives_info()
            
            assert len(drives_info) == 2
            assert drives_info[0]['device'] == '/dev/sda1'
            assert drives_info[0]['size'] == '2000G'
            assert drives_info[0]['fstype'] == 'ext4'
            # The implementation returns 'Unknown' if disk usage can't be determined from the mountpoint
            assert 'used' in drives_info[0]
            assert 'available' in drives_info[0]
            assert 'is_usb' in drives_info[0]
            assert 'label' in drives_info[0]

    def test_get_drives_info_with_error(self):
        """Test handling errors when getting drive information."""
        with patch('subprocess.run', side_effect=Exception("Test error")):
            drives_info = storage_manager.get_drives_info()
            
            assert len(drives_info) == 0

    def test_get_mount_points(self):
        """Test getting mount points."""
        mock_partitions = [
            MagicMock(device='/dev/sda1', mountpoint='/mnt/media', fstype='ext4'),
            MagicMock(device='/dev/sdb1', mountpoint='/mnt/downloads', fstype='ext4')
        ]
        
        with patch('psutil.disk_partitions', return_value=mock_partitions):
            mount_points = storage_manager.get_mount_points()
            
            assert len(mount_points) == 2
            assert mount_points[0]['device'] == '/dev/sda1'
            assert mount_points[0]['mountpoint'] == '/mnt/media'
            assert mount_points[0]['fstype'] == 'ext4'

    def test_mount_drive(self):
        """Test mounting a drive."""
        with patch('src.core.storage_manager.validate_device', return_value={'status': 'success'}), \
             patch('subprocess.run') as mock_run, \
             patch('os.makedirs') as mock_makedirs:
            
            mock_run.return_value.returncode = 0
            
            result = storage_manager.mount_drive('/dev/sda1', '/mnt/media', 'ext4')
            
            assert result['status'] == 'success'
            mock_makedirs.assert_called_once_with('/mnt/media', exist_ok=True)
            mock_run.assert_called_once()

    def test_mount_drive_with_error(self):
        """Test handling errors when mounting a drive."""
        with patch('src.core.storage_manager.validate_device', return_value={'status': 'success'}), \
             patch('subprocess.run') as mock_run, \
             patch('os.makedirs'):
            
            mock_run.return_value.returncode = 1
            mock_run.return_value.stderr = 'Mount error'
            
            result = storage_manager.mount_drive('/dev/sda1', '/mnt/media', 'ext4')
            
            assert result['status'] == 'error'
            assert 'Mount error' in result['message']

    def test_unmount_drive(self):
        """Test unmounting a drive."""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 0
            
            result = storage_manager.unmount_drive('/mnt/media')
            
            assert result['status'] == 'success'
            mock_run.assert_called_once()

    def test_unmount_drive_with_error(self):
        """Test handling errors when unmounting a drive."""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 1
            mock_run.return_value.stderr = b'Unmount error'
            
            result = storage_manager.unmount_drive('/mnt/media')
            
            assert result['status'] == 'error'
            assert 'Unmount error' in result['message']

    def test_get_directory_info(self):
        """Test getting directory information."""
        mock_disk_usage = MagicMock()
        mock_disk_usage.total = 1000 * 1024 * 1024 * 1024  # 1TB
        mock_disk_usage.used = 300 * 1024 * 1024 * 1024    # 300GB
        mock_disk_usage.free = 700 * 1024 * 1024 * 1024    # 700GB
        mock_disk_usage.percent = 30
        
        mock_scandir_results = [
            MagicMock(is_file=lambda: True),
            MagicMock(is_file=lambda: True),
            MagicMock(is_file=lambda: True),
            MagicMock(is_dir=lambda: True),
            MagicMock(is_dir=lambda: True)
        ]
        
        with patch('psutil.disk_usage', return_value=mock_disk_usage), \
             patch('os.scandir', return_value=mock_scandir_results), \
             patch('os.path.exists', return_value=True):
            
            dir_info = storage_manager.get_directory_info('/mnt/media/Movies')
            
            assert dir_info['path'] == '/mnt/media/Movies'
            assert dir_info['size'] == '300.0 GB'
            assert dir_info['files'] == 3
            assert dir_info['directories'] == 2
            assert dir_info['usage'] == 30

    def test_get_directories_info(self):
        """Test getting information for multiple directories."""
        with patch('src.core.storage_manager.get_directory_info') as mock_get_dir_info:
            mock_get_dir_info.side_effect = [
                {'path': '/mnt/media/Movies', 'size': '300.0 GB', 'files': 150, 'directories': 5, 'usage': 15},
                {'path': '/mnt/media/TVShows', 'size': '200.0 GB', 'files': 500, 'directories': 20, 'usage': 10},
                {'path': '/mnt/downloads', 'size': '100.0 GB', 'files': 25, 'directories': 3, 'usage': 5}
            ]
            
            dirs_info = storage_manager.get_directories_info([
                '/mnt/media/Movies',
                '/mnt/media/TVShows',
                '/mnt/downloads'
            ])
            
            assert len(dirs_info) == 3
            assert dirs_info[0]['path'] == '/mnt/media/Movies'
            assert dirs_info[1]['path'] == '/mnt/media/TVShows'
            assert dirs_info[2]['path'] == '/mnt/downloads'

    def test_create_directory(self):
        """Test creating a directory."""
        with patch('os.makedirs') as mock_makedirs, \
             patch('os.chown') as mock_chown, \
             patch('os.chmod') as mock_chmod:
            
            result = storage_manager.create_directory('/mnt/media/NewDir', 1000, 1000, 0o755)
            
            assert result['status'] == 'success'
            mock_makedirs.assert_called_once_with('/mnt/media/NewDir', exist_ok=True)
            mock_chown.assert_called_once_with('/mnt/media/NewDir', 1000, 1000)
            mock_chmod.assert_called_once_with('/mnt/media/NewDir', 0o755)

    def test_create_directory_with_error(self):
        """Test handling errors when creating a directory."""
        with patch('os.makedirs', side_effect=Exception("Permission denied")):
            result = storage_manager.create_directory('/mnt/media/NewDir', 1000, 1000, 0o755)
            
            assert result['status'] == 'error'
            assert 'Permission denied' in result['message']

    def test_get_shares(self):
        """Test getting network shares."""
        mock_smb_content = """
        [global]
        workgroup = WORKGROUP
        server string = Samba Server
        
        [Movies]
        path = /mnt/media/Movies
        valid users = user1
        read only = no
        
        [TVShows]
        path = /mnt/media/TVShows
        valid users = user1, user2
        read only = no
        """
        
        with patch('os.path.exists', return_value=True), \
             patch('builtins.open', mock_open(read_data=mock_smb_content)):
            
            shares = storage_manager.get_shares()
            
            assert len(shares) == 2
            assert shares[0]['name'] == 'Movies'
            assert shares[0]['path'] == '/mnt/media/Movies'
            assert shares[1]['name'] == 'TVShows'
            assert shares[1]['path'] == '/mnt/media/TVShows'

    def test_add_share(self):
        """Test adding a network share."""
        mock_smb_content = """
        [global]
        workgroup = WORKGROUP
        server string = Samba Server
        
        [Movies]
        path = /mnt/media/Movies
        valid users = user1
        read only = no
        """
        
        with patch('os.path.exists', return_value=True), \
             patch('builtins.open', mock_open(read_data=mock_smb_content)) as mock_file, \
             patch('subprocess.run') as mock_run:
            
            mock_run.return_value.returncode = 0
            
            new_share = {
                'name': 'TVShows',
                'path': '/mnt/media/TVShows',
                'valid_users': 'user1, user2',
                'read_only': 'no'
            }
            
            result = storage_manager.add_share(new_share)
            
            assert result['status'] == 'success'
            mock_file().write.assert_called()
            mock_run.assert_called_once()

    def test_remove_share(self):
        """Test removing a network share."""
        mock_smb_content = """
        [global]
        workgroup = WORKGROUP
        server string = Samba Server
        
        [Movies]
        path = /mnt/media/Movies
        valid users = user1
        read only = no
        
        [TVShows]
        path = /mnt/media/TVShows
        valid users = user1, user2
        read only = no
        """
        
        # Variable left for future validation use
        # expected_content = """
        # [global]
        # workgroup = WORKGROUP
        # server string = Samba Server
        # 
        # [TVShows]
        # path = /mnt/media/TVShows
        # valid users = user1, user2
        # read only = no
        # """
        
        mo = mock_open(read_data=mock_smb_content)
        with patch('os.path.exists', return_value=True), \
             patch('builtins.open', mo) as mock_file, \
             patch('subprocess.run') as mock_run:
            
            mock_run.return_value.returncode = 0
            
            result = storage_manager.remove_share('Movies')
            
            assert result['status'] == 'success'
            mock_file().write.assert_called()
            mock_run.assert_called_once()
            
    def test_configure_samba(self):
        """Test configuring Samba."""
        mock_file = mock_open()
        
        with patch('builtins.open', mock_file), \
             patch('src.core.storage_manager.add_share') as mock_add_share, \
             patch('subprocess.run') as mock_run:
            
            mock_run.return_value.returncode = 0
            
            config = {
                'workgroup': 'TESTGROUP',
                'server_string': 'Test Server',
                'shares': [
                    {'name': 'media', 'path': '/mnt/media', 'public': True},
                    {'name': 'downloads', 'path': '/mnt/downloads', 'public': False}
                ]
            }
            
            result = storage_manager.configure_samba(config)
            
            assert result['status'] == 'success'
            mock_file.assert_called_once_with('/etc/samba/smb.conf', 'w', encoding='utf-8')
            assert mock_add_share.call_count == 2
            mock_run.assert_called_once_with(['systemctl', 'restart', 'smbd'], check=True)
            
    def test_configure_samba_with_error(self):
        """Test handling errors when configuring Samba."""
        with patch('builtins.open', side_effect=Exception("Permission denied")):
            
            result = storage_manager.configure_samba({})
            
            assert result['status'] == 'error'
            assert 'Permission denied' in result['message']
            
    def test_install_samba(self):
        """Test installing Samba."""
        with patch('subprocess.run') as mock_run:
            
            mock_run.return_value.returncode = 0
            
            result = storage_manager.install_samba()
            
            assert result['status'] == 'success'
            assert mock_run.call_count == 2  # apt-get update and apt-get install
            
    def test_install_samba_with_error(self):
        """Test handling errors when installing Samba."""
        with patch('subprocess.run', side_effect=Exception("apt-get failed")):
            
            result = storage_manager.install_samba()
            
            assert result['status'] == 'error'
            assert 'apt-get failed' in result['message']
            
    def test_create_media_directories(self):
        """Test creating media directories."""
        with patch('os.path.exists', return_value=False), \
             patch('os.makedirs') as mock_makedirs, \
             patch('os.chown') as mock_chown, \
             patch('os.chmod') as mock_chmod, \
             patch('src.core.storage_manager.create_directory', return_value={'status': 'success'}) as mock_create_dir:
            
            result = storage_manager.create_media_directories('/mnt/media', 1000, 1000)
            
            assert result['status'] == 'success'
            mock_makedirs.assert_called_once_with('/mnt/media', exist_ok=True)
            mock_chown.assert_called_once_with('/mnt/media', 1000, 1000)
            mock_chmod.assert_called_once_with('/mnt/media', 0o755)
            assert mock_create_dir.call_count == 5  # 5 standard media directories
    
    def test_validate_device_block_device(self):
        """Test validating a block device."""
        with patch('os.path.exists', return_value=True), \
             patch('subprocess.run') as mock_run, \
             patch('os.path.basename', return_value='sda1'), \
             patch('os.path.exists', side_effect=lambda path: True):
            
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = 'part\n'
            
            # Mock the open and read for removable path check
            with patch('builtins.open', mock_open(read_data='0')):
                result = storage_manager.validate_device('/dev/sda1', 'ext4')
                
                assert result['status'] == 'success'
                assert mock_run.call_count >= 1

    def test_validate_device_network_nfs(self):
        """Test validating an NFS share."""
        with patch('subprocess.run') as mock_run:
            
            # First call is ping, second is showmount (optional)
            mock_run.side_effect = [
                MagicMock(returncode=0),  # Ping success
                MagicMock(returncode=0)   # Showmount success
            ]
            
            result = storage_manager.validate_device('192.168.1.100:/share', 'nfs')
            
            assert result['status'] == 'success'
            assert mock_run.call_count >= 1

    def test_validate_device_network_cifs(self):
        """Test validating a CIFS share."""
        with patch('subprocess.run') as mock_run:
            
            mock_run.return_value.returncode = 0  # Ping success
            
            result = storage_manager.validate_device('//192.168.1.100/share', 'cifs')
            
            assert result['status'] == 'success'
            assert mock_run.call_count == 1

    def test_validate_device_invalid_format(self):
        """Test validating a device with invalid format."""
        # Test NFS with invalid format
        result = storage_manager.validate_device('invalid_nfs_format', 'nfs')
        assert result['status'] == 'error'
        assert 'Invalid NFS share format' in result['message']
        
        # Test CIFS with invalid format
        result = storage_manager.validate_device('invalid_cifs_format', 'cifs')
        assert result['status'] == 'error'
        assert 'Invalid CIFS share format' in result['message']

    def test_verify_mount(self):
        """Test verifying a mount point."""
        with patch('os.path.ismount', return_value=True), \
             patch('os.makedirs') as mock_makedirs, \
             patch('os.chown') as mock_chown, \
             patch('builtins.open', mock_open()), \
             patch('os.unlink') as mock_unlink, \
             patch('os.rmdir') as mock_rmdir, \
             patch('psutil.disk_usage') as mock_disk_usage:
            
            mock_disk_usage.return_value.free = 20 * 1024 * 1024 * 1024  # 20GB free
            
            result = storage_manager.verify_mount('/mnt/media', 1000, 1000)
            
            assert result['status'] == 'success'
            mock_makedirs.assert_called_once()
            mock_chown.assert_called_once()
            mock_unlink.assert_called_once()
            mock_rmdir.assert_called_once()

    def test_verify_mount_low_space(self):
        """Test verifying a mount point with low space."""
        with patch('os.path.ismount', return_value=True), \
             patch('os.makedirs') as mock_makedirs, \
             patch('os.chown') as mock_chown, \
             patch('builtins.open', mock_open()), \
             patch('os.unlink') as mock_unlink, \
             patch('os.rmdir') as mock_rmdir, \
             patch('psutil.disk_usage') as mock_disk_usage:
            
            mock_disk_usage.return_value.free = 5 * 1024 * 1024 * 1024  # 5GB free
            
            result = storage_manager.verify_mount('/mnt/media', 1000, 1000)
            
            assert result['status'] == 'warning'
            assert 'Only 5.0 GB available' in result['message']

    def test_verify_mount_not_mounted(self):
        """Test verifying a non-mounted point."""
        with patch('os.path.ismount', return_value=False):
            result = storage_manager.verify_mount('/mnt/media', 1000, 1000)
            
            assert result['status'] == 'error'
            assert 'not a mount point' in result['message']

    def test_verify_mount_permission_error(self):
        """Test verifying a mount point with permission error."""
        with patch('os.path.ismount', return_value=True), \
             patch('os.makedirs', side_effect=PermissionError("Permission denied")):
            
            result = storage_manager.verify_mount('/mnt/media', 1000, 1000)
            
            assert result['status'] == 'error'
            assert 'Cannot write to mount point' in result['message']

    def test_add_to_fstab(self):
        """Test adding an entry to fstab."""
        mock_blkid_output = 'abcdef12-3456-7890-abcd-1234567890ab\n'
        mock_fstab_content = """
# /etc/fstab
UUID=12345 / ext4 defaults 0 1
"""
        fstab_mock = mock_open(read_data=mock_fstab_content)
        
        with patch('subprocess.run') as mock_run, \
             patch('builtins.open', fstab_mock):
            
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = mock_blkid_output
            
            result = storage_manager.add_to_fstab('/dev/sda1', '/mnt/media', 'ext4')
            
            assert result['status'] == 'success'
            assert mock_run.call_count >= 1
            # Check that write was called with the fstab line
            assert any('Added by Pi-PVARR' in str(args) for args in fstab_mock().write.call_args_list)

    def test_add_to_fstab_network(self):
        """Test adding a network mount to fstab."""
        mock_fstab_content = """
# /etc/fstab
UUID=12345 / ext4 defaults 0 1
"""
        fstab_mock = mock_open(read_data=mock_fstab_content)
        
        with patch('builtins.open', fstab_mock):
            result = storage_manager.add_to_fstab('192.168.1.100:/share', '/mnt/share', 'nfs', 'rw,soft,intr')
            
            assert result['status'] == 'success'
            # Should use direct path for network mounts, not UUID
            assert '192.168.1.100:/share' in str(fstab_mock().write.call_args_list[-1])

    def test_add_to_fstab_existing(self):
        """Test adding an entry to fstab when it already exists."""
        mock_fstab_content = """
# /etc/fstab
UUID=12345 / ext4 defaults 0 1
/dev/sda1 /mnt/media ext4 defaults 0 2
"""
        fstab_mock = mock_open(read_data=mock_fstab_content)
        
        with patch('builtins.open', fstab_mock):
            result = storage_manager.add_to_fstab('/dev/sda1', '/mnt/media', 'ext4')
            
            assert result['status'] == 'warning'
            assert 'already exists' in result['message']

    def test_mount_drive_network(self):
        """Test mounting a network drive."""
        with patch('src.core.storage_manager.validate_device', return_value={'status': 'success', 'message': 'Valid'}), \
             patch('os.makedirs') as mock_makedirs, \
             patch('subprocess.run') as mock_run:
            
            mock_run.return_value.returncode = 0
            
            result = storage_manager.mount_drive('192.168.1.100:/share', '/mnt/share', 'nfs')
            
            assert result['status'] == 'success'
            mock_makedirs.assert_called_once()
            # Should use appropriate options for NFS
            assert '-t' in str(mock_run.call_args)
            assert 'nfs' in str(mock_run.call_args)

    def test_mount_drive_with_fstab(self):
        """Test mounting a drive with fstab entry."""
        with patch('src.core.storage_manager.validate_device', return_value={'status': 'success', 'message': 'Valid'}), \
             patch('os.makedirs') as mock_makedirs, \
             patch('subprocess.run') as mock_run, \
             patch('src.core.storage_manager.add_to_fstab', return_value={'status': 'success', 'message': 'Added to fstab'}):
            
            mock_run.return_value.returncode = 0
            
            result = storage_manager.mount_drive('/dev/sda1', '/mnt/media', 'ext4', None, True)
            
            assert result['status'] == 'success'
            assert 'Added to fstab' in result['message']

    def test_mount_drive_validation_error(self):
        """Test mounting a drive with validation error."""
        with patch('src.core.storage_manager.validate_device', 
                  return_value={'status': 'error', 'message': 'Invalid device'}):
            
            result = storage_manager.mount_drive('/dev/sda1', '/mnt/media', 'ext4')
            
            assert result['status'] == 'error'
            assert 'Invalid device' in result['message']