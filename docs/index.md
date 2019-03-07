
# Overview


<nav class="toc">
  <h2>Rule sets</h2>
  <ul>
    <li><a href="#debug">debug Rules</a></li>
    <li><a href="#subpar">Build self-contained python executables.</a></li>
  </ul>
</nav>

<h2><a href="./debug.html" id="debug">debug Rules</a></h2>

<h3>Macros</h3>
<table class="overview-table">
  <colgroup>
    <col class="col-name" />
    <col class="col-description" />
  </colgroup>
  <tbody>
    <tr>
      <td>
        <a href="./debug.html#dump">
          <code>dump</code>
        </a>
      </td>
      <td>
        <p>Debugging method that recursively prints object fields to stderr</p>

      </td>
    </tr>
  </tbody>
</table>
<h2><a href="./subpar.html" id="subpar">Build self-contained python executables.</a></h2>

<h3>Rules</h3>
<table class="overview-table">
  <colgroup>
    <col class="col-name" />
    <col class="col-description" />
  </colgroup>
  <tbody>
    <tr>
      <td>
        <a href="./subpar.html#parfile">
          <code>parfile</code>
        </a>
      </td>
      <td>
        <p>A self-contained, single-file Python program, with a .par file extension.</p>

      </td>
    </tr>
    <tr>
      <td>
        <a href="./subpar.html#parfile_test">
          <code>parfile_test</code>
        </a>
      </td>
      <td>
        <p>Identical to par_binary, but the rule is marked as being a test.</p>

      </td>
    </tr>
  </tbody>
</table>
<h3>Macros</h3>
<table class="overview-table">
  <colgroup>
    <col class="col-name" />
    <col class="col-description" />
  </colgroup>
  <tbody>
    <tr>
      <td>
        <a href="./subpar.html#par_binary">
          <code>par_binary</code>
        </a>
      </td>
      <td>
        <p>An executable Python program.</p>

      </td>
    </tr>
    <tr>
      <td>
        <a href="./subpar.html#par_test">
          <code>par_test</code>
        </a>
      </td>
      <td>
        <p>An executable Python test.</p>

      </td>
    </tr>
  </tbody>
</table>
