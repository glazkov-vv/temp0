import tempfile
import pytest
import os
from logic.file import File
from logic.workspace import Workspace
from logic.transactions import *

@pytest.fixture
def setupdir():
    global tmpdir
    tmpdir=tempfile.mkdtemp(suffix="td")
    
    global tmpdir_file
    tmpdir_file=File.fromPath(tmpdir)

    os.mkdir(os.path.join(tmpdir,"A"))
    os.mkdir(os.path.join(tmpdir,"A","B"))
    os.mkdir(os.path.join(tmpdir,"A","C"))
    with open(os.path.join(tmpdir,"A","C","x.txt"),"w") as f:
        f.write("1")

    with open(os.path.join(tmpdir,"A","B","y.txt"),"w") as f:
        f.write("11")
    global wspace
    wspace=Workspace(tmpdir)

@pytest.mark.asyncio
async def test_copy_removal(setupdir):
    cpath=os.path.join(tmpdir,"A","C")
    
    c1=CopyTransaction(Selection([cpath]),os.path.join(tmpdir,"A","B"))
    await c1.execute()
    assert(os.path.getsize(os.path.join(tmpdir,'A',"B","C","x.txt"))==1) 
    
    await c1.revert().execute()
    assert(not os.path.exists(os.path.join(tmpdir,"A","B","C")))

@pytest.mark.asyncio
async def test_copy(setupdir):
    cpath=os.path.join(tmpdir,"A","C")
    
    c1=CopyTransaction(Selection([cpath]),os.path.join(tmpdir,"A","B"))
    await c1.execute()
    assert(os.path.getsize(os.path.join(tmpdir,'A',"B","C","x.txt"))==1) 
    
    await c1.revert().execute()
    assert(not os.path.exists(os.path.join(tmpdir,"A","B","C")))

@pytest.mark.asyncio
async def test_move(setupdir):
    cpath=os.path.join(tmpdir,"A","C")
    
    c1=MoveTransaction(Selection([cpath]),os.path.join(tmpdir,"A","B"))
    await c1.execute()
    assert(os.path.getsize(os.path.join(tmpdir,'A',"B","C","x.txt"))==1) 
    assert(not os.path.exists(os.path.join(tmpdir,"A","C")))

    await c1.revert().execute()
    assert(not os.path.exists(os.path.join(tmpdir,"A","B","C")))
    assert(os.path.exists(os.path.join(tmpdir,"A","C")))


@pytest.mark.asyncio
async def test_change_permissions_and_unsuccessful_move(setupdir):
    cpath=os.path.join(tmpdir,"A","C")
    cperm=File.fromPath(cpath).get_permissions()
    nperm=[True,False,True]*3
    c1=ChangePermissionTransaction(cpath,cperm,nperm)
    await c1.execute()
    assert(File.fromPath(cpath).get_permissions()==nperm)
    
    c2=MoveTransaction(Selection([cpath]),os.path.join(tmpdir,"A","B"))
    res=await c2.execute()
    assert(res!=None)

    await c1.revert().execute()
    #assert(File.fromPath(cpath).get_permissions()==cperm)

@pytest.mark.asyncio
async def test_change_permissions_and_unsuccessful_copy_and_remove(setupdir):
    cpath=os.path.join(tmpdir,"A","C")
    xpath=os.path.join(tmpdir,"A","C","x.txt")
    xperm=File.fromPath(xpath).get_permissions()
    nperm=[False,True,True]*3
    c1=ChangePermissionTransaction(xpath,xperm,nperm)
    await c1.execute()
    
    c2=CopyTransaction(Selection([cpath]),os.path.join(tmpdir,"A","B"))
    res=await c2.execute()
    assert(res!=None)
    await c1.revert().execute()

    await c1.revert().execute()
    Ypath=os.path.join(tmpdir,"A","C","Y")

    os.mkdir(Ypath)
    with open(os.path.join(Ypath,"y.txt"),"w"):
        pass

    c3=ChangePermissionTransaction(Ypath,File.fromPath(Ypath).get_permissions(),[True,True,False]*3)
    await c3.execute()
    c4=CopyTransaction(Selection([cpath]),os.path.join(tmpdir,"A"))
    res=await c4.execute()
    assert(res != None)
    
    c5=RemoveTransaction(Selection([Ypath]))
    res=await c5.execute()
    assert (res!=None)

    await c3.revert().execute()

    c5=RemoveTransaction(Selection([Ypath]))
    res=await c5.execute()
    assert(not os.path.exists(Ypath))
    

